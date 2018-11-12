from ._base import ControlCommand


class Command(ControlCommand):

    help = 'Shutdown uWSGI instance'

    def add_arguments(self, parser):

        super(Command, self).add_arguments(parser)

        parser.add_argument(
            '--force', action='store_true', dest='force',
            help='Use forced (brutal) shutdown instead of a graceful one.',
        )

    def get_cmd(self, options):
        return b'Q' if options['force'] else b'q'
