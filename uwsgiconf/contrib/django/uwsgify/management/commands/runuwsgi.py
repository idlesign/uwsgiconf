import inspect
from os.path import dirname, basename

from django.core.management.base import BaseCommand

from ...toolbox import run_uwsgi, SectionMutator


class Command(BaseCommand):

    help = 'Runs uWSGI to serve your project'

    @classmethod
    def find_base_dir(cls):
        """Runs up the stack to find the location of manage.py
        which will be considered a project base path.

        :rtype: str|unicode
        """
        frame = inspect.currentframe()

        while True:
            frame = frame.f_back
            fname = frame.f_globals['__file__']

            if basename(fname) == 'manage.py':
                break

        return dirname(fname)

    def handle(self, *args, **options):
        dir_base = self.find_base_dir()
        section = SectionMutator.run(dir_base)
        run_uwsgi(section)
