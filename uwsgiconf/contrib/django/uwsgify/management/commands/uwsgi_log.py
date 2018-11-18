from ._base import FifoCommand


class Command(FifoCommand):

    help = 'Allows managing of uWSGI log related stuff'

    def add_arguments(self, parser):

        super(Command, self).add_arguments(parser)

        parser.add_argument(
            '--reopen', action='store_true', dest='reopen',
            help='Reopen log file. Could be required after third party rotation.',
        )
        parser.add_argument(
            '--rotate', action='store_true', dest='rotate',
            help='Trigger built-in log rotation.',
        )

    def run_cmd(self, fifo, options):
        fifo.cmd_log(reopen=options['reopen'], rotate=options['rotate'])
