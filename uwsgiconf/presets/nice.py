from ..config import Section as _Section


class Section(_Section):
    """Basic nice configuration."""

    def __init__(self, name=None, touch_reload=None, workers=None, threads=None, mules=None, **kwargs):
        """

        :param str|unicode name: Section name.

        :param str|list touch_reload: Reload uWSGI if the specified file or directory is modified/touched.

        :param int workers: Spawn the specified number of workers (processes).
            Default: workers number equals to CPU count.

        :param int threads: Number of threads per worker.

        :param int mules: Number of mules to spawn.

        :param kwargs:
        """
        super(Section, self).__init__(strict_config=True, name=name, **kwargs)

        # Fix possible problems with non-ASCII.
        self.env('LANG', 'en_US.UTF-8')

        if touch_reload:
            self.main_process.set_basic_params(touch_reload=touch_reload)

        if workers:
            self.workers.set_basic_params(count=workers)
        else:
            self.workers.set_count_auto()

        self.workers.set_thread_params(count=threads)
        self.workers.set_mules_params(mules=mules)
        self.workers.set_harakiri_params(verbose=True)
        self.main_process.set_basic_params(vacuum=True)
        self.main_process.set_naming_params(autonaming=True)
        self.master_process.set_basic_params(enable=True)
        self.locks.set_basic_params(thunder_lock=True)


class PythonSection(Section):
    """Basic nice configuration using Python plugin."""

    def __init__(self, name=None, params_python=None, wsgi_module=None, embedded_plugins=True, **kwargs):
        """

        :param str|unicode name: Section name.

        :param dict params_python: See Python plugin basic params.

        :param str|unicode wsgi_module: WSGI application module path or filepath.

            Example:
                mypackage.my_wsgi_module -- read from `application` attr of mypackage/my_wsgi_module.py
                mypackage.my_wsgi_module:my_app -- read from `my_app` attr of mypackage/my_wsgi_module.py

        :param bool|None embedded_plugins: This indicates whether plugins were embedded into uWSGI,
            which is the case if you have uWSGI from PyPI.

        :param kwargs:
        """
        if embedded_plugins is True:
            embedded_plugins = self.embedded_plugins_presets.BASIC + ['python', 'python2', 'python3']

        super(PythonSection, self).__init__(name=name, embedded_plugins=embedded_plugins, **kwargs)

        self.python.set_basic_params(**(params_python or {}))

        if wsgi_module:
            self.python.set_wsgi_params(module=wsgi_module)
