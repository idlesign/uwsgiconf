from os import path

from django.core.management.base import BaseCommand

from uwsgiconf.sysinit import get_config, TYPE_SYSTEMD
from uwsgiconf.utils import Finder
from ...toolbox import SectionMutator


class Command(BaseCommand):

    help = 'Generates configuration files for Systemd, Upstart, etc.'

    def add_arguments(self, parser):

        super(Command, self).add_arguments(parser)

        parser.add_argument(
            '--systype', dest='systype',
            help='System type alias to make configuration for. E.g.: systemd, upstart.',
        )

        parser.add_argument(
            '--nostatic', action='store_true', dest='nostatic',
            help='Tells uWSGI to NOT to serve static and media files.',
        )

    def handle(self, *args, **options):
        systype = options['systype'] or TYPE_SYSTEMD

        mutator = SectionMutator.spawn()
        command = 'manage.py uwsgi_run'

        if options['nostatic']:
            command = command + ' --nostatic'

        config = get_config(
            systype,
            conf=mutator.section,
            conf_path=path.join(mutator.dir_base, command),
            runner=Finder.python(),
        )

        print(config)
