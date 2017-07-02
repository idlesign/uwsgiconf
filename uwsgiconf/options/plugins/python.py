import sys

from ...base import PluginOptionsGroupBase
from ...exceptions import ConfigurationError


AUTO = (1,)


class PythonPlugin(PluginOptionsGroupBase):
    """Python plugin options."""

    def set_basic_params(self, version=AUTO, python_home=None, enable_threads=None, search_path=None,
                         python_binary=None, tracebacker_path=None,
                         plugin_dir=None, **kwargs):
        """

        :param str|unicode|int version: Python version plugin supports.

            Example:
                    3 - version 3
                    <empty> - version 2
                    <default> - version deduced by uwsgiconf

        :param str|unicode python_home: set python executable directory - PYTHONHOME/virtualenv

        :param str|unicode search_path: add directory (or an .egg or a glob) to the Python search path.
            This can be specified up to 64 times.

        :param str|unicode python_binary: set python program name

        :param str|unicode tracebacker_path: enable the uWSGI Python tracebacker
            http://uwsgi-docs.readthedocs.io/en/latest/Tracebacker.html

        :param str|unicode plugin_dir: directory to search for plugin

        :param bool enable_threads: Enable threads in the embedded languages.
            This will allow to spawn threads in your app.
            Threads will simply *not work* if this option is not enabled. There will likely be no error,
            just no execution of your thread code.

        """
        self.name = self.get_name(version)

        self._section.grp_workers.set_thread_params(enable_threads=enable_threads)
        self._set('py-tracebacker', tracebacker_path)
        self._set('py-program-name', python_binary)
        self._set('pyhome', python_home)
        self._set('pythonpath', search_path, multi=True)

        return super(PythonPlugin, self).set_basic_params(plugin_dir=plugin_dir, **kwargs)

    def get_name(self, version):
        """Returns plugin name."""

        name = 'python'

        if version:
            if version is AUTO:
                version = sys.version_info[0]

                if version == 2:
                    version = ''

            name = '%s%s' % (name, version)

        return name

    def set_app_args(self, *args):
        """manually set ``sys.argv`` for python apps.

        pyargv="one two three" will set ``sys.argv`` to ``('one', 'two', 'three')``.

        :param args:
        """
        if args:
            self._set('pyargv', ' '.join(args))

        return self._section

    def set_wsgi_params(self, module=None, callable_name=None):
        """

        :param str|unicode module:
            * load .wsgi file as the Python application
            * load a WSGI module as the application.
              The module (sans ``.py``) must be importable, ie. be in ``PYTHONPATH``.

            Example:
                mypackage.my_wsgi_module -- read from `application` attr of mypackage/my_wsgi_module.py
                mypackage.my_wsgi_module:my_app -- read from `my_app` attr of mypackage/my_wsgi_module.py

        :param str|unicode callable_name: set WSGI callable name. Default: application

        """
        module = module or ''

        if '/' in module:
            self._set('wsgi-file', module)

        else:
            self._set('wsgi', module)

        self._set('callable', callable_name)

        return self._section

    def eval_wsgi_entrypoint(self, code):
        """Evaluate Python code as WSGI entry point

        :param str|unicode code:
        """
        self._set('eval', code)

        return self._section

    def set_autoreload_params(self, scan_interval=None, ignore_modules=None):
        """

        :param int scan_interval: Monitor Python modules' modification times to trigger reload.

            WARNING: use only in development.

            Modification scan interval given in seconds.

        :param list|st|unicode ignore_modules: ignore the specified module during auto-reload scan

        """
        self._set('py-auto-reload', scan_interval)
        self._set('py-auto-reload-ignore', ignore_modules, multi=True)

        return self._section

    def register_module_alias(self, alias, module_path, after_init=False):
        """add a python alias module

        http://uwsgi-docs.readthedocs.io/en/latest/PythonModuleAlias.html

        :param str|unicode alias:
        :param str|unicode module_path:
        :param bool after_init: add a python module alias after uwsgi module initialization
        """
        command = 'post-pymodule-alias' if after_init else 'pymodule-alias'
        self._set(command, '%s=%s' % (alias, module_path), multi=True)

        return self._section

    def import_module(self, modules, shared=False, into_spooler=False):
        """import a python module

        :param list|str|unicode modules:

        :param bool shared: import a python module in all of the processes

        :param bool into_spooler: import a python module in the spooler

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
        """Run a Python script in the uWSGI environment

        :param str|unicode module:

        """
        self._set('pyrun', module)

        return self._section
