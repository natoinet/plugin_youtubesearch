from django.utils import timezone
from django.db import models
from django.contrib.postgres.fields import JSONField

from tucat.application.models import TucatElement
from tucat.core.models import TucatTask

from tucat.plugin_youtubesearch.api import GoogleAPIClient

class SuggestedQuery(TucatElement):
    query = models.CharField(max_length=200, default='')
    language = models.CharField(max_length=5, default='fr')
    country = models.CharField(max_length=5, default='FR')
    client = models.CharField(max_length=20, default='firefox')
    site = models.CharField(max_length=5, default='yt')

    def __str__(self):
        return self.query

    def get_url(self):
        # TODO Add APIKEY to .env
        api_key = GoogleAPIClient().api_key

        # https://codepen.io/tayfunerbilen/pen/rIHvD
        # https://gist.github.com/eristoddle/3750993
        # https://stackoverflow.com/questions/5102878/google-suggest-api
        # https://shreyaschand.com/blog/2013/01/03/google-autocomplete-api/
        #url = "https://suggestqueries.google.com/complete/search?hl="+self.locale+"&client="+self.client+"&q="+self.query+"&ds=yt&json=t&key="+api_key
        url = "https://suggestqueries.google.com/complete/search?ds=yt&json=t"

        return url + "&client=" + self.client + "&hl=" + self.language \
                + "&cr=" + self.country + "&q=" + self.query + "&key=" + api_key

    class Meta:
        abstract = False

class SuggestedQueryResult(models.Model):
    query = models.ForeignKey(SuggestedQuery, models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    result = JSONField()

    def __str__(self):
        return str(self.result)

    @classmethod
    def create(cls, query, result):
        suggested_query_result = cls(query=query, result=result)
        return suggested_query_result

class YouTubeQueryResult(models.Model):
    query = models.CharField(max_length=200, default='')
    suggested_query_result = models.ForeignKey(SuggestedQueryResult, models.CASCADE)
    search_result = JSONField(default=dict)
    videos_result = JSONField(default=dict)

    def __str__(self):
        return str(self.query)

    @classmethod
    def create(cls, query, suggested_query_result, result):
        youtube_query_result = cls(query=query, suggested_query_result=suggested_query_result, search_result=result)
        return youtube_query_result
