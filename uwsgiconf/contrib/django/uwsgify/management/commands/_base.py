import os

from django.core.management.base import BaseCommand, CommandError

from ...toolbox import find_project_dir, get_project_name, SectionMutator


class FifoCommand(BaseCommand):
    """Base for uWSGI control management commands using master FIFO."""

    def get_cmd(self, options):
        """Must return FIFO command.

        :param dict options:
        :rtype: bytes

        """
        raise NotImplementedError

    def handle(self, *args, **options):

        project_name = get_project_name(find_project_dir())

        filepath = SectionMutator.get_fifo_filepath(project_name)

        if os.path.exists(filepath):

            with open(filepath, 'wb') as f:
                f.write(self.get_cmd(options))

        else:
            raise CommandError(
                'Unable to find uWSGI FIFO file for "%s" project in %s' % (project_name, filepath))
