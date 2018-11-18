import os

from django.core.management.base import BaseCommand, CommandError

from uwsgiconf.utils import Fifo
from ...toolbox import find_project_dir, get_project_name, SectionMutator


class FifoCommand(BaseCommand):
    """Base for uWSGI control management commands using master FIFO."""

    def run_cmd(self, fifo, options):
        """Must return FIFO command.

        :param Fifo fifo:
        :param dict options:
        :rtype: bytes

        """
        raise NotImplementedError

    def handle(self, *args, **options):

        project_name = get_project_name(find_project_dir())

        filepath = SectionMutator.get_fifo_filepath(project_name)
        fifo = Fifo(filepath)

        if os.path.exists(filepath):

            self.run_cmd(fifo, options)

        else:
            raise CommandError(
                'Unable to find uWSGI FIFO file for "%s" project in %s' % (project_name, filepath))
