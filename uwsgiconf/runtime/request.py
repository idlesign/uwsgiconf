from .. import uwsgi


class _Request(object):

    __slots__ = []

    @property
    def env(self):
        """Request environment dictionary."""
        return uwsgi.env

    @property
    def id(self):
        """Returns current request number (handled by worker on core).

        :rtype: int
        """
        return uwsgi.request_id()

    @property
    def total_count(self):
        """Returns the total number of requests managed so far by the pool of uWSGI workers.

        :rtype: int
        """
        return uwsgi.total_requests()

    @property
    def fd(self):
        """Returns current request file descriptor.

        :rtype: int
        """
        return uwsgi.connection_fd()

    @property
    def content_length(self):
        """Returns current post content length.

        :rtype: int|long
        """
        return uwsgi.cl()

    def log(self):
        """Instructs uWSGI to log current request data.

        :rtype: None
        """
        uwsgi.log_this_request()

    def add_var(self, name, value):
        """Registers custom request variable.

        Can be used for better integration with the internal routing subsystem.

        :param str|unicode name:

        :param str|unicode value:

        :rtype: bool

        :raises ValueError: If buffer size is not enough.
        """
        return uwsgi.add_var(name, value)
