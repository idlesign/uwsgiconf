from ._base import FifoCommand


class Command(FifoCommand):

    help = 'Dump uWSGI configuration and current stats into the log'

    def get_cmd(self, options):
        return b's'
