import sys

from ..base import OptionsGroup
from ..exceptions import ConfigurationError


AUTO = (1,)


class Python(OptionsGroup):
    """Python plugin options.

    .. note:: By default the plugin does not initialize the GIL.
        This means your app-generated threads will not run.
        If you need threads, remember to enable them with ``enable_threads``.

    """

    plugin = True

    def set_basic_params(
            self, version=AUTO, python_home=None, enable_threads=None, search_path=None,
            python_binary=None, tracebacker_path=None, plugin_dir=None, **kwargs):
        """

        :param str|unicode|int version: Python version plugin supports.

            Example:
                * 3 - version 3
                * <empty> - version 2
                * <default> - version deduced by uwsgiconf

        :param str|unicode python_home: Set python executable directory - PYTHONHOME/virtualenv.

        :param str|unicode search_path: Add directory (or an .egg or a glob) to the Python search path.

            .. note:: This can be specified up to 64 times.

        :param str|unicode python_binary: Set python program name.

        :param str|unicode tracebacker_path: Enable the uWSGI Python tracebacker.
            http://uwsgi-docs.readthedocs.io/en/latest/Tracebacker.html

        :param str|unicode plugin_dir: Directory to search for plugin.

        :param bool enable_threads: Enable threads in the embedded languages.
            This will allow to spawn threads in your app.

            .. warning:: Threads will simply *not work* if this option is not enabled.
                         There will likely be no error, just no execution of your thread code.

        """
        self._set_name(version)

        self._section.workers.set_thread_params(enable=enable_threads)
        self._set('py-tracebacker', tracebacker_path)
        self._set('py-program-name', python_binary)
        self._set('pyhome', python_home)
        self._set('pythonpath', search_path, multi=True)

        self._section.set_plugins_params(search_dirs=plugin_dir)

        return self._section

    def _set_name(self, version=AUTO):
        """Returns plugin name."""

        name = 'python'

        if version:
            if version is AUTO:
                version = sys.version_info[0]

                if version == 2:
                    version = ''

            name = '%s%s' % (name, version)

        self.name = name

    def _get_name(self, *args, **kwargs):
        name = self.name

        if not name:
            self._set_name()

        return self.name

    def set_app_args(self, *args):
        """Sets ``sys.argv`` for python apps.

        Examples:
            * pyargv="one two three" will set ``sys.argv`` to ``('one', 'two', 'three')``.

        :param args:
        """
        if args:
            self._set('pyargv', ' '.join(args))

        return self._section

    def set_wsgi_params(self, module=None, callable_name=None):
        """Set wsgi related parameters.

        :param str|unicode module:
            * load .wsgi file as the Python application
            * load a WSGI module as the application.

            .. note:: The module (sans ``.py``) must be importable, ie. be in ``PYTHONPATH``.

            Examples:
                * mypackage.my_wsgi_module -- read from `application` attr of mypackage/my_wsgi_module.py
                * mypackage.my_wsgi_module:my_app -- read from `my_app` attr of mypackage/my_wsgi_module.py

        :param str|unicode callable_name: Set WSGI callable name. Default: application.

        """
        module = module or ''

        if '/' in module:
            self._set('wsgi-file', module)

        else:
            self._set('wsgi', module)

        self._set('callable', callable_name)

        return self._section

    def eval_wsgi_entrypoint(self, code):
        """Evaluates Python code as WSGI entry point.

        :param str|unicode code:
        """
        self._set('eval', code)

        return self._section

    def set_autoreload_params(self, scan_interval=None, ignore_modules=None):
        """Sets autoreload related parameters.

        :param int scan_interval: Seconds. Monitor Python modules' modification times to trigger reload.

            .. warning:: Use only in development.

        :param list|st|unicode ignore_modules: Ignore the specified module during auto-reload scan.

        """
        self._set('py-auto-reload', scan_interval)
        self._set('py-auto-reload-ignore', ignore_modules, multi=True)

        return self._section

    def register_module_alias(self, alias, module_path, after_init=False):
        """Adds an alias for a module.

        http://uwsgi-docs.readthedocs.io/en/latest/PythonModuleAlias.html

        :param str|unicode alias:
        :param str|unicode module_path:
        :param bool after_init: add a python module alias after uwsgi module initialization
        """
        command = 'post-pymodule-alias' if after_init else 'pymodule-alias'
        self._set(command, '%s=%s' % (alias, module_path), multi=True)

        return self._section

    def import_module(self, modules, shared=False, into_spooler=False):
        """Imports a python module.

        :param list|str|unicode modules:

        :param bool shared: Import a python module in all of the processes.

        :param bool into_spooler: Import a python module in the spooler.
            http://uwsgi-docs.readthedocs.io/en/latest/Spooler.html

        """
        if all((shared, into_spooler)):
            raise ConfigurationError('Unable to set both `shared` and `into_spooler` flags')

        if into_spooler:
            command = 'spooler-python-import'
        else:
            command = 'shared-python-import' if shared else 'python-import'

        self._set(command, modules, multi=True)

        return self._section

    def run_module(self, module):
        """Runs a Python script in the uWSGI environment.

        :param str|unicode module:

        """
        self._set('pyrun', module)

        return self._section
