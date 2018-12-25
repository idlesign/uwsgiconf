import os

from django.core.management.base import BaseCommand, CommandError

from uwsgiconf.utils import Fifo
from ...toolbox import SectionMutator


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
        mutator = SectionMutator.spawn()
        filepath = mutator.get_fifo_filepath()

        fifo = Fifo(filepath)

        if os.path.exists(filepath):

            self.run_cmd(fifo, options)

        else:
            raise CommandError(
                'Unable to find uWSGI FIFO file for "%s" project in %s' %
                (mutator.section.project_name, filepath))
