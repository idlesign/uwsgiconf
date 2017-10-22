from ..base import OptionsGroup


class Applications(OptionsGroup):
    """Applications.

    """

    def set_basic_params(
            self, exit_if_none=None, max_per_worker=None, single_interpreter=None, no_default=None):
        """

        :param bool exit_if_none: Exit if no app can be loaded.

        :param int max_per_worker: Set the maximum number of per-worker applications.

        :param bool single_interpreter: Do not use multiple interpreters (where available).
            Some of the supported languages (such as Python) have the concept of "multiple interpreters".
            By default every app is loaded in a new python interpreter (that means a pretty-well isolated
            namespace for each app). If you want all of the app to be loaded in the same python vm,
            use the this option.

        :param bool no_default: Do not fallback to default app.

        """

        self._set('need-app', exit_if_none, cast=bool)
        self._set('max-apps', max_per_worker)
        self._set('single-interpreter', single_interpreter, cast=bool)
        self._set('no-default-app', no_default, cast=bool)

        return self._section

    def mount(self, mountpoint, app, into_worker=False):
        """Load application under mountpoint.

        Example:
            * .mount('/app1', 'app1.py')
            * .mount('example.com', 'app2.py')
            * .mount('the_app3', 'app3.py')
            * .mount('/pinax/here', '/var/www/pinax/deploy/pinax.wsgi')

        * http://uwsgi-docs.readthedocs.io/en/latest/Nginx.html#hosting-multiple-apps-in-the-same-process-aka-managing-script-name-and-path-info

        :param str|unicode mountpoint: Host name, URL part, etc.

        :param str|unicode app: App module/file.

        :param bool into_worker: Load application under mountpoint
            in the specified worker or after workers spawn.

        """
        # todo check worker mount -- uwsgi_init_worker_mount_app() expects worker://
        self._set('worker-mount' if into_worker else 'mount', '%s=%s' % (mountpoint, app), multi=True)

        return self._section

    def switch_into_lazy_mode(self, affect_master=None):
        """Load apps in workers instead of master.

        This option may have memory usage implications
        as Copy-on-Write semantics can not be used.

        .. note:: Consider using ``touch_chain_reload`` option in ``workers`` basic params
            for lazy apps reloading.

        :param bool affect_master: If **True** only workers will be
          reloaded by uWSGI's reload signals; the master will remain alive.

          .. warning:: uWSGI configuration changes are not picked up on reload by the master.


        """
        self._set('lazy' if affect_master else 'lazy-apps', True, cast=bool)

        return self._section
