from __future__ import absolute_import

import logging
import csv

from django.conf import settings
from django.utils import timezone
from django.core.files import File

from celery import task
from celery.app.task import Task

import requests

from tucat.core.celery import app
from tucat.core.models import DjangoAdminCeleryTaskLock
from tucat.application.models import TucatApplication
from tucat.plugin_youtubesearch.models import InitialQuery, SuggestedQueryResult, YouTubeQueryResult, YouTubeQueryResultExport
from tucat.plugin_youtubesearch.api import call_youtube_search_list_api, call_youtube_videos_list_api


logger = logging.getLogger('plugins')

def do_task_cmd(action=None, obj=None):
    try:
        logger.info('do_task_cmd')
        one_app = TucatApplication.objects.get(pk=obj.pk)

        if (action is 'run'):
            logger.info('Running')
            do_run.apply_async((obj.pk,))
            one_app.update(status='r')
        elif (action is 'stop'):
            logger.info('Stopping')

            one_app.update(status='s')
        else:
            logger.info('Unknown command')
            one_app.update(status='f')

    except Exception as e:
        logger.exception(e)
        one_app.update(status='f')

@task
def do_run(obj_pk):
    try:
        logger.info('do_run %s', obj_pk)

        db_name = __package__.replace('.', '_')
        one_app = TucatApplication.objects.get(pk=obj_pk)
        one_app.update(status='r')

        queries = InitialQuery.objects.filter(application_id=one_app.id, is_enabled=True)

        for element in queries:
            logger.info('do_run %s', element.query)
            do_run_google_suggest_query(element.pk)

        one_app.update(status='c')

        logger.info('do_run google_suggest_queries success')
    except Exception as e:
        logger.exception(e)
        one_app.update(status='f')

    finally:
        logger.info('file:%s | finally', __file__)

def do_run_google_suggest_query(query_pk):
    try:
        logger.debug('do_run_google_suggest_query')

        query = InitialQuery.objects.get(pk=query_pk)
        query_url = query.get_url()
        logger.debug('do_run_google_suggest_query query_url %s', query_url)

        response = requests.get(query_url)

        if (response.ok):
            result = response.json()
            #suggestions = [i for i in result[1]]
            suggested_query_result = SuggestedQueryResult.create(query, result)
            suggested_query_result.save()
            logger.info("do_run_google_suggest_query - Requests is ok : %s %s %s", response.status_code, response.url, result)

            do_run_youtube_search_list_api(suggested_query_result.pk)
        else:
            logger.error("do_run_google_suggest_query - Requests is not ok : %s %s %s", response.url, response.status_code, response.history)
            raise

    except Exception as e:
        logger.exception(e)
        raise

def do_run_youtube_search_list_api(suggested_query_result_pk):
    try:
        logger.debug('do_run_youtube_search_list_api %s', suggested_query_result_pk)

        suggested_query = SuggestedQueryResult.objects.get(pk=suggested_query_result_pk)

        logger.info('do_run_youtube_search_list_api results before calling api %s', str(suggested_query))

        # Call Youtube API for all queries
        for query in suggested_query.result[1]:
            search_result = call_youtube_search_list_api(query)
            yt_query_result = YouTubeQueryResult.create(query, suggested_query, search_result)
            yt_query_result.save()

            do_run_youtube_videos_api(yt_query_result.pk)

    except Exception as e:
        logger.exception(e)
        raise

def do_run_youtube_videos_api(yt_query_result_pk):
    try:
        logger.debug('do_run_youtube_api %s', yt_query_result_pk)

        youtube_query_result = YouTubeQueryResult.objects.get(pk=yt_query_result_pk)

        list_video_ids = [ item['id']['videoId'] for item in youtube_query_result.search_result['items'] if 'videoId' in item['id'] ]
        str_video_ids = ",".join(list_video_ids)

        videos_result = call_youtube_videos_list_api(str_video_ids)

        youtube_query_result.videos_result = videos_result
        youtube_query_result.save()

    except Exception as e:
        logger.exception(e)
        raise

def do_export_plugin_youtubesearch_cmd(action=None, obj=None):
    logger.info('do_export_plugin_youtubesearch_cmd %s %s', action, obj)

    if (action is 'run'):
        logger.info('do_export_plugin_youtubesearch_cmd running')
        do_run_export.apply_async((obj.pk,))

    elif (action is 'stop'):
        logger.info('do_export_plugin_youtubesearch_cmd stopping')
        do_stop_export(obj.pk)

    else:
        logger.info('do_export_plugin_youtubesearch_cmd Unknown command')

@task(bind=True)
def do_run_export(self, obj_pk):

    logger.info('do_run_export %s', obj_pk)
    export = YouTubeQueryResultExport.objects.get(pk=obj_pk)

    try:
        export.update(self.request.id, 'r')

        # Get all YTQR whose FK points to SGQR
        youtube_queryset = YouTubeQueryResult.objects.filter(suggested_query_result=export.suggested_query_result)

        out_folder = str(settings.APPS_DIR.path('media')) + '/output'
        filename = 'suggested_netvizz_' + export.name + timezone.now().strftime("_%Y-%m-%d_%Hh%Mm%Ss") + '.tab'

        with open(out_folder  + '/' + filename, 'w+') as f:
            generate_csv(youtube_queryset, f)
            export.file = File(f)
            export.save()

        export.update(self.request.id, 'c')


    except Exception as e:
        logger.exception(e)
        export.update(self.request.id, 'f')

def generate_csv(youtube_queryset, f):
    try:
        logger.info('generate_csv')

        #writer = csv.writer(f, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer = csv.writer(f, delimiter='\t')

        headers = ['query', 'position', 'channelId', 'channelTitle', \
                    'videoId', 'publishedAt', 'videoTitle', 'videoDescription', \
                    'videoCategoryId', 'duration', 'dimension', 'definition', \
                    'caption', 'licensedContent', 'viewCount', 'likeCount', \
                    'dislikeCount', 'favoriteCount', 'commentCount']

        writer.writerow(headers)

        for yt_query_result in youtube_queryset:
            for i, item in enumerate(yt_query_result.videos_result['items']):
                row = [
                        yt_query_result.query,
                        i + 1,
                        item['snippet'].get('channelId', ''),
                        item['snippet'].get('channelTitle', ''),
                        item['id'],
                        item['snippet'].get('publishedAt', ''),
                        item['snippet'].get('title', ''),
                        item['snippet'].get('description', ''),
                        item['snippet'].get('categoryId', ''),
                        item['contentDetails'].get('duration', ''),
                        item['contentDetails'].get('dimension', ''),
                        item['contentDetails'].get('definition', ''),
                        item['contentDetails'].get('caption', ''),
                        item['contentDetails'].get('licensedContent', ''),
                        item['statistics'].get('viewCount', ''),
                        item['statistics'].get('likeCount', ''),
                        item['statistics'].get('dislikeCount', ''),
                        item['statistics'].get('favoriteCount', ''),
                        item['statistics'].get('commentCount', '')
                    ]
                writer.writerow(row)
        logger.info('generate_csv Finished')

    except Exception as e:
        logger.exception(e)
        raise

def do_stop_export(obj_pk):
    logger.info('do_stop_export')
    export = SuggestedQueryResult.objects.get(pk=obj_pk)

    try:
        logger.info('do_stop_export locked task_id %s', export.task_id)
        app.control.revoke(export.task_id, terminate=True)
        logger.info('do_stop_export: Task revoked')

        export.update('', 's')

    except Exception as e:
        logger.exception(e)
