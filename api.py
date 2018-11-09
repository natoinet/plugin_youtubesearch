import logging

from django.conf import settings

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import environ


logger = logging.getLogger('plugins')

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class GoogleAPIClient(metaclass=Singleton):
    def __init__(self):
        try:
            ROOT_DIR = environ.Path(__file__) - 3
            env = environ.Env(DEBUG=(bool, False),)
            api_name = 'youtube'
            api_version = 'v3'
            self.api_key = env('GOOGLE_API_KEY')
            self.service = build(api_name, api_version, developerKey=self.api_key)
        except Exception as e:
            logger.exception(e)
            raise

'''
def get_google_api_service(scopes, api_name, api_version):
    #json_filename = join(environ['PATH_BASE'], environ['GOOGLE_API_PRIVATE_FILE'])
    json_filename = str(settings.ROOT_DIR.path('config/private/')) + 'seotrafico-pagespeed-7f4041e0b7f4.json'

    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_filename, scopes=scopes)
    http_auth = credentials.authorize(Http())
    service = build(api_name, api_version, http=http_auth, cache_discovery=False)

    return service
'''

def call_youtube_search_list_api(query):
    try:
        logger.debug('call_youtube_search_list_api %s', query)

        part='id,snippet'

        youtube = GoogleAPIClient().service
        search_response = youtube.search().list(q=query, part=part).execute()

        return search_response
    except Exception as e:
        logger.exception(e)
        raise

def call_youtube_videos_list_api(video_ids):
    try:
        logger.info('call_youtube_videos_list_api %s', video_ids)

        part = 'id,contentDetails,liveStreamingDetails,localizations,snippet,statistics,status,topicDetails'

        youtube = GoogleAPIClient().service
        search_response = youtube.videos().list(part=part, id=video_ids).execute()

        return search_response
    except Exception as e:
        logger.exception(e)
        raise
