from ._base import FifoCommand


class Command(FifoCommand):

    help = 'Reloads uWSGI master process, workers'

    def add_arguments(self, parser):

        super(Command, self).add_arguments(parser)

        parser.add_argument(
            '--force', action='store_true', dest='force',
            help='Use forced (brutal) reload instead of a graceful one.',
        )
        parser.add_argument(
            '--workers-only', action='store_true', dest='workers',
            help='Reload only workers.',
        )
        parser.add_argument(
            '--workers-chain', action='store_true', dest='chain',
            help='Run chained workers reload (one after another, instead of destroying all of them in bulk).',
        )

    def run_cmd(self, fifo, options):
        fifo.cmd_reload(
            force=options['force'],
            workers_only=options['workers'],
            workers_chain=options['chain'],
        )
