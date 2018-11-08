import logging

from django.conf import settings

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import environ


logger = logging.getLogger('plugins')

def get_api_key():
    ROOT_DIR = environ.Path(__file__) - 3
    env = environ.Env(DEBUG=(bool, False),) # set default values and casting
    return env('GOOGLE_API_KEY')


def get_google_api_service(api_name, api_version):
    try:
        logger.debug('get_google_api_service')
        api_key = get_api_key()
        service = build(api_name, api_version, developerKey=api_key)

        return service
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

def call_youtube_api(query):
    #scopes = ['https://www.googleapis.com/auth/youtube.readonly']
    api_name = 'youtube'
    api_version = 'v3'

    try:
        logger.debug('call_youtube_api %s', query)

        youtube = get_google_api_service(api_name, api_version)
        search_response = youtube.search().list(q=query, part='id,snippet').execute()
        return search_response
    except Exception as e:
        logger.exception(e)
        raise
