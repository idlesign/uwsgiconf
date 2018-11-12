from django.core.management.base import BaseCommand

from ...toolbox import run_uwsgi, SectionMutator, find_project_dir


class Command(BaseCommand):

    help = 'Runs uWSGI to serve your project'

    def add_arguments(self, parser):

        super(Command, self).add_arguments(parser)

        parser.add_argument(
            '--nostatic', action='store_false', dest='use_static_handler',
            help='Tells uWSGI to NOT to serve static and media files.',
        )

    def handle(self, *args, **options):
        dir_base = find_project_dir()
        section = SectionMutator.run(dir_base=dir_base, options=options)
        run_uwsgi(section)
