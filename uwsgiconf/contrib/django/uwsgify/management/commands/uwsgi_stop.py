from ._base import FifoCommand


class Command(FifoCommand):

    help = 'Shutdown uWSGI instance'

    def add_arguments(self, parser):

        super(Command, self).add_arguments(parser)

        parser.add_argument(
            '--force', action='store_true', dest='force',
            help='Use forced (brutal) shutdown instead of a graceful one.',
        )

    def run_cmd(self, fifo, options):
        fifo.cmd_stop(force=options['force'])
