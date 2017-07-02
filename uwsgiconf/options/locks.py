from ..base import OptionsGroup


class Locks(OptionsGroup):
    """Locks.

    http://uwsgi.readthedocs.io/en/latest/Locks.html

    """

    def set_basic_params(self, count=None, thunder_lock=None, lock_engine=None):
        """

        :param int count: create the specified number of shared locks

        :param bool thunder_lock: serialize accept() usage (if possible)
            Could improve performance on Linux with robust pthread mutexes.

            http://uwsgi.readthedocs.io/en/latest/articles/SerializingAccept.html

        :param str|unicode lock_engine: set the lock engine

            Example:
                - ipcsem

        """
        self._set('thunder-lock', thunder_lock, cast=bool)
        self._set('lock-engine', lock_engine)
        self._set('locks', count)

        return self._section

    def set_thread_ipcsem_params(self, ftok=None):
        """

        :param str|unicode ftok: set the ipcsem key via ftok() for avoiding duplicates
        """
        self._set('ftok', ftok)

        return self._section

    def lock_file(self, fpath, after_setup=False, wait=False):
        """lock the specified file

        :param str|unicode fpath:

        :param bool after_setup:
            True  - after logging/daemon setup
            False - before starting

        :param bool wait:
            True  - wait if locked
            False - exit if locked

        """
        command = 'flock-wait' if wait else 'flock'

        if after_setup:
            command = '%s2' % command

        self._set(command, fpath)

        return self._section
