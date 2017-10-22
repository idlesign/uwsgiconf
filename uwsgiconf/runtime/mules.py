from .. import uwsgi
from ..utils import decode


class Mule(object):
    """Represents uWSGI Mule."""

    __slots__ = ['id']

    def __init__(self, id):
        """
        :param int id: Mule ID

        """
        self.id = id

    @classmethod
    def get_current_id(cls):
        """Returns current mule ID.

        :rtype: int
        """
        return uwsgi.mule_id()

    @classmethod
    def get_message(cls, signals=True, farms=False, buffer_size=65536, timeout=-1):
        """Block until a mule message is received and return it.

        This can be called from multiple threads in the same programmed mule.

        :param bool signals: Whether to manage signals.

        :param bool farms: Whether to manage farms.

        :param int buffer_size:

        :param int timeout: Seconds.

        :rtype: str|unicode

        :raises ValueError: If not in a mule.
        """
        return decode(uwsgi.mule_get_msg(signals, farms, buffer_size, timeout))

    def send(self, message):
        """Sends a message to a mule(s)/farm.

        :param str|unicode message:

        :rtype: bool

        :raises ValueError: If no mules, or mule ID or farm name is not recognized.
        """
        return uwsgi.mule_msg(message, self.id)


class Farm(object):
    """Represents uWSGI Mule Farm."""

    __slots__ = ['name']

    def __init__(self, name):
        """
        :param str|unicode name: Mule farm name.

        """
        self.name = name

    @property
    def is_mine(self):
        """Returns flag indicating whether current mule belongs
        to this farm.

        :param str|unicode name: Farm name.

        :rtype: bool
        """
        return uwsgi.in_farm(self.name)

    @classmethod
    def get_message(cls):
        """Reads a mule farm message.

         * http://uwsgi.readthedocs.io/en/latest/Embed.html

         .. warning:: Bytes are returned for Python 3.

         :rtype: str|unicode|None

         :raises ValueError: If not in a mule
         """
        return decode(uwsgi.farm_get_msg())

    def send(self, message):
        """Sends a message to the given farm.

        :param str|unicode message:

        """
        return uwsgi.farm_msg(self.name, message)
