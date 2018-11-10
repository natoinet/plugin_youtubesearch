import logging

from tucat.core.commands import TucatExportCommand
from tucat.plugin_youtubesearch.tasks import do_export_plugin_youtubesearch_cmd

logger = logging.getLogger('plugins')

class Command(TucatExportCommand):
    '''
    Admin > User Command > TucatExportCommand.handle > do_cmd > do_export_cmd
    '''

    def do_cmd(self, action=None, obj=None):
        logger.debug('plugin_youtubesearch export do_cmd %s %s %s', str(self), action, str(obj))
        do_export_plugin_youtubesearch_cmd(action=action, obj=obj)
