import logging

from tucat.application.commands import TucatCommand
from tucat.plugin_youtubesearch.tasks import do_task_cmd

logger = logging.getLogger('plugins')

class Command(TucatCommand):
    '''
    Admin > User Command > TucatCommand.handle > do_cmd > do_extraction_cmd
    '''

    def do_cmd(self, action=None, obj=None):
        logger.debug('plugins do_cmd %s %s %s', str(self), action, str(obj))
        do_task_cmd(action, obj=obj)
