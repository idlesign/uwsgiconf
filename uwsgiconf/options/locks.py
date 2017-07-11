from ..base import OptionsGroup


class Locks(OptionsGroup):
    """Locks.

    * http://uwsgi.readthedocs.io/en/latest/Locks.html

    """

    def set_basic_params(self, count=None, thunder_lock=None, lock_engine=None):
        """
        :param int count: Create the specified number of shared locks.

        :param bool thunder_lock: Serialize accept() usage (if possible)
            Could improve performance on Linux with robust pthread mutexes.

            http://uwsgi.readthedocs.io/en/latest/articles/SerializingAccept.html

        :param str|unicode lock_engine: Set the lock engine.

            Example:
                - ipcsem

        """
        self._set('thunder-lock', thunder_lock, cast=bool)
        self._set('lock-engine', lock_engine)
        self._set('locks', count)

        return self._section

    def set_ipcsem_params(self, ftok=None, persistent=None):
        """Sets ipcsem lock engine params.

        :param str|unicode ftok: Set the ipcsem key via ftok() for avoiding duplicates.

        :param bool persistent: Do not remove ipcsem's on shutdown.

        """
        self._set('ftok', ftok)
        self._set('persistent-ipcsem', persistent, cast=bool)

        return self._section

    def lock_file(self, fpath, after_setup=False, wait=False):
        """Locks the specified file.

        :param str|unicode fpath: File path.

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
