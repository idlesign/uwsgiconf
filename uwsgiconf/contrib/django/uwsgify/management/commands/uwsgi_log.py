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

    def get_cmd(self, options):

        result = b''

        if options['reopen']:
            result += b'l'

        if options['rotate']:
            result += b'L'

        return result
