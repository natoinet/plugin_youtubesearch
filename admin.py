import logging

from django.contrib import admin
from django.contrib.sites.shortcuts import get_current_site
from django.core.management import call_command
from django.http import FileResponse
from django.utils.html import format_html

from tucat.plugin_youtubesearch.models import InitialQuery, \
                                                SuggestedQueryResult, \
                                                YouTubeQueryResult, \
                                                YouTubeQueryResultExport
from tucat.core.admin import run, stop, download, test

logger = logging.getLogger('plugins')

class InitialQueryAdmin(admin.ModelAdmin):
    readonly_fields = ('modified', 'status')
    list_display = ('query', 'language', 'country', 'is_enabled')

class SuggestedQueryResultAdmin(admin.ModelAdmin):
    list_display = ('get_suggested', 'initial', 'get_language', 'get_country', 'date')

    def get_suggested(self, obj):
        if len(obj.result) > 0 :
            return " - ".join( [i for i in obj.result[1]] )
        else:
            return str(obj.result)
    get_suggested.short_description = 'Suggested results'
    get_suggested.admin_order_field = 'suggested_query_result__initial__language'

    def get_language(self, obj):
        return obj.initial.language
    get_language.short_description = 'Language'
    get_language.admin_order_field = 'suggested_query_result__initial__language'

    def get_country(self, obj):
        return obj.initial.country
    get_country.short_description = 'Country'
    get_country.admin_order_field = 'suggested_query_result__initial__country'

class YouTubeQueryResultAdmin(admin.ModelAdmin):
    list_display = ('query', 'get_date', 'get_initial', 'get_language', \
                    'get_country')

    def get_date(self, obj):
        return obj.suggested_query_result.date
    get_date.short_description = 'Date'
    get_date.admin_order_field = 'suggested_query_result__date'

    def get_initial(self, obj):
        return obj.suggested_query_result.initial
    get_initial.short_description = 'Initial'
    get_initial.admin_order_field = 'suggested_query_result__initial'

    def get_language(self, obj):
        return obj.suggested_query_result.initial.language
    get_language.short_description = 'Language'
    get_language.admin_order_field = 'suggested_query_result__initial__language'

    def get_country(self, obj):
        return obj.suggested_query_result.initial.country
    get_country.short_description = 'Country'
    get_country.admin_order_field = 'suggested_query_result__initial__country'

class YouTubeQueryResultExportAdmin(admin.ModelAdmin):
    actions = [run, stop, download]

    readonly_fields = ('task_id', 'status', 'file',)
    list_display = ('name', 'get_date', 'get_initial', 'get_language', \
                    'get_country', 'status', 'download')

    def get_date(self, obj):
        return obj.suggested_query_result.date
    get_date.short_description = 'Date'
    get_date.admin_order_field = 'suggested_query_result__date'

    def get_initial(self, obj):
        return obj.suggested_query_result.initial
    get_initial.short_description = 'Initial'
    get_initial.admin_order_field = 'suggested_query_result__initial'

    def get_language(self, obj):
        return obj.suggested_query_result.initial.language
    get_language.short_description = 'Language'
    get_language.admin_order_field = 'suggested_query_result__initial__language'

    def get_country(self, obj):
        return obj.suggested_query_result.initial.country
    get_country.short_description = 'Country'
    get_country.admin_order_field = 'suggested_query_result__initial__country'

    class Media:
        # Adds the js script to the HTML admin view
        # https://docs.djangoproject.com/en/2.1/topics/forms/media/
        js = ("js/project.js",)

    def download(self, obj):
        button_html = '<button type="submit" class="button" type="button" \
                        onclick="download_file(%d)">Download</button>' % obj.id
        return format_html(button_html)

    class Meta:
        abstract = False


admin.site.register(InitialQuery, InitialQueryAdmin)
admin.site.register(YouTubeQueryResult, YouTubeQueryResultAdmin)
admin.site.register(SuggestedQueryResult, SuggestedQueryResultAdmin)
admin.site.register(YouTubeQueryResultExport, YouTubeQueryResultExportAdmin)
