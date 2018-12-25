from django.core.management.base import BaseCommand

from ...toolbox import run_uwsgi, SectionMutator


class Command(BaseCommand):

    help = 'Runs uWSGI to serve your project'

    def add_arguments(self, parser):

        super(Command, self).add_arguments(parser)

        parser.add_argument(
            '--nostatic', action='store_false', dest='use_static_handler',
            help='Tells uWSGI to NOT to serve static and media files.',
        )
        parser.add_argument(
            '--compile', action='store_true', dest='compile',
            help='Do not run just print out compiled uWSGI .ini configuration.',
        )

    def handle(self, *args, **options):
        mutator = SectionMutator.spawn(options=options)
        run_uwsgi(mutator.section, compile_only=options['compile'])
