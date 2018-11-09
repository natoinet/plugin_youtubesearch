from __future__ import absolute_import

import logging

from django.conf import settings
from django.utils import timezone

from celery import task
from celery.app.task import Task

import requests

from tucat.core.celery import app
from tucat.core.models import DjangoAdminCeleryTaskLock
from tucat.application.models import TucatApplication
from tucat.plugin_youtubesearch.models import SuggestedQuery, SuggestedQueryResult, YouTubeQueryResult
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

        queries = SuggestedQuery.objects.filter(application_id=one_app.id, is_enabled=True)

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

        query = SuggestedQuery.objects.get(pk=query_pk)
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
