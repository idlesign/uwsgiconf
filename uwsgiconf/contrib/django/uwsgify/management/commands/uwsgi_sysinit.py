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
            help='Tells uWSGI to NOT to serve static and media files.',
        )

    def handle(self, *args, **options):
        systype = options['systype'] or TYPE_SYSTEMD

        mutator = SectionMutator.spawn()

        config = get_config(
            systype,
            conf=mutator.section,
            conf_path=path.join(mutator.dir_base, 'manage.py uwsgi_run --nostatic'),
            runner=Finder.python(),
        )

        print(config)
