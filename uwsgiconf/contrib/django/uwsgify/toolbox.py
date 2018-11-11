import os


if False:  # pragma: nocover
    from uwsgiconf.base import Section


class SectionMutator(object):
    """Configuration file section mutator."""

    def __init__(self, section, dir_base, project_name):
        # todo maybe integrate envbox
        from django.conf import settings

        self.section = section
        self.dir_base = dir_base
        self.project_name = project_name
        self.settings = settings

    @classmethod
    def run(cls, dir_base):
        """Alternative constructor. Creates a mutator and returns section object.

        :param str|unicode dir_base:
        :rtype: Section

        """
        from uwsgiconf.utils import ConfModule

        name_module = ConfModule.default_name
        name_project = os.path.basename(dir_base)
        path_conf = os.path.join(dir_base, name_module)

        if os.path.exists(path_conf):
            # Read an existing config for further modification of first section.
            section = cls._get_section_existing(name_module, name_project)

        else:
            # Create section on-fly.
            section = cls._get_section_new(dir_base)

        wrapped = cls(section, dir_base, name_project)
        wrapped.mutate()

        return section

    @classmethod
    def _get_section_existing(self, name_module, name_project):
        """Loads config section from existing configuration file (aka uwsgicfg.py)

        :param str|unicode name_module:
        :param str|unicode name_project:
        :rtype: Section

        """
        from importlib import import_module

        from uwsgiconf.settings import CONFIGS_MODULE_ATTR

        config = getattr(
            import_module(os.path.splitext(name_module)[0], package=name_project),
            CONFIGS_MODULE_ATTR)[0]

        return config.sections[0]

    @classmethod
    def _get_section_new(cls, dir_base):
        """Creates a new section with default settings.

        :param str|unicode dir_base:
        :rtype: Section

        """
        from uwsgiconf.presets.nice import PythonSection

        section = PythonSection(
            wsgi_module='%s/wsgi.py' % dir_base,

        ).networking.register_socket(
            PythonSection.networking.sockets.http('127.0.0.1:8000')
        )

        return section

    def contribute_static(self):
        """Contributes static and media file serving settings to an existing section."""
        from django.core import management

        settings = self.settings
        statics = self.section.statics
        statics.register_static_map(settings.STATIC_URL, settings.STATIC_ROOT)
        statics.register_static_map(settings.MEDIA_URL, settings.MEDIA_ROOT)

        management.call_command('collectstatic', clear=True, interactive=False)

    def contribute_error_pages(self):
        """Contributes generic static error massage pages to an existing section."""

        self.section.routing.set_error_pages(
            common_prefix=os.path.join(self.settings.STATIC_ROOT, 'uwsgify'))

    def mutate(self):
        """Mutates current section."""
        section = self.section

        main = section.main_process
        main.set_owner_params(os.getuid(), os.getegid())
        main.set_naming_params(prefix='[%s] ' % self.project_name)

        # todo maybe autoreload in debug

        apps = section.applications
        apps.set_basic_params(
            no_default=True,
            manage_script_name=True,
        )

        self.contribute_error_pages()
        self.contribute_static()


def run_uwsgi(config_section):
    """Runs uWSGI using the given section configuration.

    :param Section config_section:

    """
    config_path = config_section.as_configuration().tofile()
    os.execvp('uwsgi', ['uwsgi', '--ini=%s' % config_path])
