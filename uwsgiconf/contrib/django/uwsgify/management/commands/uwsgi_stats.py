from ._base import FifoCommand


class Command(FifoCommand):

    help = 'Dump uWSGI configuration and current stats into the log'

    def run_cmd(self, fifo, options):
        fifo.cmd_stats()
