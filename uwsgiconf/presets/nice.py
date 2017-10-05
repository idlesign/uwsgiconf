from ..config import Section as _Section


class Section(_Section):
    """Basic nice configuration."""

    def __init__(
            self, name=None, touch_reload=None, workers=None, threads=None, mules=None, owner=None,
            log_into=None, process_prefix=None, **kwargs):
        """

        :param str|unicode name: Section name.

        :param str|list touch_reload: Reload uWSGI if the specified file or directory is modified/touched.

        :param int workers: Spawn the specified number of workers (processes).
            Default: workers number equals to CPU count.

        :param int|bool threads: Number of threads per worker or ``True`` to enable user-made threads support.

        :param int mules: Number of mules to spawn.

        :param str|unicode owner: Set process owner user and group.

        :param str|unicode log_into: Filepath or UDP address to send logs into.

        :param str|unicode process_prefix: Add prefix to process names.

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

        set_threads = self.workers.set_thread_params

        if isinstance(threads, bool):
            set_threads(enable=threads)

        else:
            set_threads(count=threads)

        self.workers.set_mules_params(mules=mules)
        self.workers.set_harakiri_params(verbose=True)
        self.main_process.set_basic_params(vacuum=True)
        self.main_process.set_naming_params(
            autonaming=True,
            prefix='%s ' % process_prefix if process_prefix else None,
        )
        self.master_process.set_basic_params(enable=True)
        self.master_process.set_exit_events(sig_term=True)  # Respect the convention. Make Upstart and Co happy.
        self.locks.set_basic_params(thunder_lock=True)
        self.configure_owner(owner=owner)
        self.logging.log_into(target=log_into)

    def configure_owner(self, owner='www-data'):
        """Shortcut to set process owner data.

        :param str|unicode owner: Sets user and group. Default: ``www-data``.

        """
        if owner is not None:
            self.main_process.set_owner_params(uid=owner, gid=owner)

        return self


class PythonSection(Section):
    """Basic nice configuration using Python plugin."""

    def __init__(
            self, name=None, params_python=None, wsgi_module=None, embedded_plugins=True,
            require_app=True, **kwargs):
        """

        :param str|unicode name: Section name.

        :param dict params_python: See Python plugin basic params.

        :param str|unicode wsgi_module: WSGI application module path or filepath.

            Example:
                mypackage.my_wsgi_module -- read from `application` attr of mypackage/my_wsgi_module.py
                mypackage.my_wsgi_module:my_app -- read from `my_app` attr of mypackage/my_wsgi_module.py

        :param bool|None embedded_plugins: This indicates whether plugins were embedded into uWSGI,
            which is the case if you have uWSGI from PyPI.

        :param bool require_app: Exit if no app can be loaded.

        :param kwargs:
        """
        if embedded_plugins is True:
            embedded_plugins = self.embedded_plugins_presets.BASIC + ['python', 'python2', 'python3']

        super(PythonSection, self).__init__(name=name, embedded_plugins=embedded_plugins, **kwargs)

        self.python.set_basic_params(**(params_python or {}))

        if wsgi_module:
            self.python.set_wsgi_params(module=wsgi_module)

        self.applications.set_basic_params(exit_if_none=require_app)
