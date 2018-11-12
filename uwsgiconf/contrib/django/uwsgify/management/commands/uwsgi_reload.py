from ._base import ControlCommand


class Command(ControlCommand):

    help = 'Reloads uWSGI master process, workers'

    def add_arguments(self, parser):

        super(Command, self).add_arguments(parser)

        parser.add_argument(
            '--force', action='store_true', dest='force',
            help='Use forced (brutal) reload instead of a graceful one.',
        )
        parser.add_argument(
            '--workers-only', action='store_true', dest='workers',
            help='Only reload workers.',
        )

    def get_cmd(self, options):
        forced = options['force']

        if options['workers']:
            return b'R' if forced else b'r'

        return b'R' if forced else b'r'
