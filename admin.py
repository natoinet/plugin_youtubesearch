import logging

from django.contrib import admin

from tucat.plugin_youtubesearch.models import SuggestedQuery, SuggestedQueryResult, YouTubeQueryResult


logger = logging.getLogger('plugins')


class SuggestedQueryAdmin(admin.ModelAdmin):
    readonly_fields = ('modified', 'status')
    list_display = ('query', 'language', 'country', 'is_enabled')

class YouTubeQueryResultAdmin(admin.ModelAdmin):
    list_display = ('query', 'get_date', 'get_parent', 'get_language', 'get_country')

    def get_date(self, obj):
        return obj.suggested_query_result.date
    get_date.short_description = 'Date'
    get_date.admin_order_field = 'suggested_query_result__date'

    def get_parent(self, obj):
        return obj.suggested_query_result.query
    get_parent.short_description = 'Parent'
    get_parent.admin_order_field = 'suggested_query_result__query'

    def get_language(self, obj):
        return obj.suggested_query_result.query.language
    get_language.short_description = 'Language'
    get_language.admin_order_field = 'suggested_query_result__query__language'

    def get_country(self, obj):
        return obj.suggested_query_result.query.country
    get_country.short_description = 'Country'
    get_country.admin_order_field = 'suggested_query_result__query__country'

admin.site.register(SuggestedQuery, SuggestedQueryAdmin)
admin.site.register(YouTubeQueryResult, YouTubeQueryResultAdmin)
admin.site.register(SuggestedQueryResult)
