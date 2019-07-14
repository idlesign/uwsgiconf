import inspect
import os


if False:  # pragma: nocover
    from uwsgiconf.base import Section


def find_project_dir():
    """Runs up the stack to find the location of manage.py
    which will be considered a project base path.

    :rtype: str|unicode
    """
    frame = inspect.currentframe()

    while True:
        frame = frame.f_back
        fname = frame.f_globals['__file__']

        if os.path.basename(fname) == 'manage.py':
            break

    return os.path.dirname(fname)


def get_project_name(project_dir):
    """Return project name from project directory.

    :param str|unicode project_dir:
    :rtype: str|unicode
    """
    return os.path.basename(project_dir)


class SectionMutator(object):
    """Configuration file section mutator."""

    def __init__(self, section, dir_base, project_name, options):
        # todo maybe integrate envbox
        from django.conf import settings

        self.section = section  # type: Section
        self.dir_base = dir_base
        self.project_name = project_name
        self.settings = settings
        self.options = options

    @property
    def runtime_dir(self):
        """Project runtime directory.

        :rtype: str

        """
        return self.section.replace_placeholders('{project_runtime_dir}')

    def get_pid_filepath(self):
        """Return pidfile path for the given project.

        :param str|unicode project_name:
        :rtype: str|unicode

        """
        return os.path.join(self.runtime_dir, 'uwsgi.pid')

    def get_fifo_filepath(self):
        """Return master FIFO path for the given project.

        :param str|unicode project_name:
        :rtype: str|unicode

        """
        return os.path.join(self.runtime_dir, 'uwsgi.fifo')

    @classmethod
    def spawn(cls, options=None, dir_base=None):
        """Alternative constructor. Creates a mutator and returns section object.

        :param dict options:
        :param str|unicode dir_base:

        :rtype: SectionMutator

        """
        from uwsgiconf.utils import ConfModule

        options = options or {
            'compile': True,
        }

        dir_base = os.path.abspath(dir_base or find_project_dir())

        name_module = ConfModule.default_name
        name_project = get_project_name(dir_base)
        path_conf = os.path.join(dir_base, name_module)

        if os.path.exists(path_conf):
            # Read an existing config for further modification of first section.
            section = cls._get_section_existing(path_conf, name_module, name_project)

        else:
            # Create section on-fly.
            section = cls._get_section_new(dir_base)

        mutator = cls(
            section=section,
            dir_base=dir_base,
            project_name=name_project,
            options=options)

        mutator.mutate()

        return mutator

    @classmethod
    def _get_section_existing(self, path_conf, name_module, name_project):
        """Loads config section from existing configuration file (aka uwsgicfg.py)

        :param str|unicode path_conf:
        :param str|unicode name_module:
        :param str|unicode name_project:
        :rtype: Section

        """
        from uwsgiconf.utils import PY3
        from uwsgiconf.settings import CONFIGS_MODULE_ATTR

        def load():
            module_fake_name = '%s.%s' % (name_project, os.path.splitext(name_module)[0])

            if not PY3:  # pragma: nocover
                import imp
                return imp.load_source(module_fake_name, path_conf)

            import importlib.util

            spec = importlib.util.spec_from_file_location(module_fake_name, path_conf)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            return module

        config = getattr(load(), CONFIGS_MODULE_ATTR)[0]

        return config.sections[0]

    @classmethod
    def _get_section_new(cls, dir_base):
        """Creates a new section with default settings.

        :param str|unicode dir_base:
        :rtype: Section

        """
        from uwsgiconf.presets.nice import PythonSection
        from django.conf import settings

        wsgi_app = settings.WSGI_APPLICATION

        app_package, filename, _, = wsgi_app.split('.')

        def get_wsgi_path(base):
            return os.path.join(base, app_package, '%s.py' %filename)

        path_wsgi = get_wsgi_path(dir_base)

        if not os.path.exists(path_wsgi):
            # Maybe dir_base already contains app_package.
            path_wsgi = get_wsgi_path(os.path.dirname(dir_base))

        section = PythonSection(
            wsgi_module=path_wsgi,

        ).networking.register_socket(
            PythonSection.networking.sockets.http('127.0.0.1:8000')

        ).main_process.change_dir(dir_base)

        return section

    def contribute_static(self):
        """Contributes static and media file serving settings to an existing section."""

        options = self.options
        if options['compile'] or not options['use_static_handler']:
            return

        from django.core.management import call_command

        settings = self.settings
        statics = self.section.statics
        statics.register_static_map(settings.STATIC_URL, settings.STATIC_ROOT)
        statics.register_static_map(settings.MEDIA_URL, settings.MEDIA_ROOT)

        call_command('collectstatic', clear=True, interactive=False)

    def contribute_error_pages(self):
        """Contributes generic static error massage pages to an existing section."""

        static_dir = self.settings.STATIC_ROOT

        if not static_dir:
            # Source static directory is not configured. Use temporary.
            import tempfile
            static_dir = os.path.join(tempfile.gettempdir(), self.project_name)
            self.settings.STATIC_ROOT = static_dir

        self.section.routing.set_error_pages(
            common_prefix=os.path.join(static_dir, 'uwsgify'))

    def contribute_runtime_dir(self):
        section = self.section

        if not section.get_runtime_dir(default=False):
            # If runtime directory is not set by user, let's try use system default.
            section.set_runtime_dir(section.get_runtime_dir())

            if not self.options['compile']:
                os.makedirs(self.runtime_dir, 0o755, True)

    def mutate(self):
        """Mutates current section."""
        section = self.section
        project_name = self.project_name

        section.project_name = project_name

        self.contribute_runtime_dir()

        main = section.main_process
        main.set_naming_params(prefix='[%s] ' % project_name)

        main.set_pid_file(
            self.get_pid_filepath(),
            before_priv_drop=False,  # For vacuum to cleanup properly.
            safe=True,
        )

        section.master_process.set_basic_params(
            fifo_file=self.get_fifo_filepath(),
        )

        # todo maybe autoreload in debug

        apps = section.applications
        apps.set_basic_params(
            manage_script_name=True,
        )

        self.contribute_error_pages()
        self.contribute_static()


def run_uwsgi(config_section, compile_only=False):
    """Runs uWSGI using the given section configuration.

    :param Section config_section:
    :param bool compile_only: Do not run, only compile and output configuration file for run.

    """
    config = config_section.as_configuration()

    if compile_only:
        config.print_ini()
        return

    from uwsgiconf.utils import UwsgiRunner

    UwsgiRunner.prepare_env()  # Use uwsgi command from venv if any.

    config_path = config.tofile()
    os.execvp('uwsgi', ['uwsgi', '--ini=%s' % config_path])
