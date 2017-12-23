from ..config import Section
from ..utils import filter_locals


class Broodlord(object):
    """This mode is a way for a vassal to ask for reinforcements to the Emperor.

    Reinforcements are new vassals spawned on demand generally bound on the same socket.

    .. warning:: If you are looking for a way to dynamically adapt the number
        of workers of an instance, check the Cheaper subsystem - adaptive process spawning mode.

        *Broodlord mode is for spawning totally new instances.*

    * http://uwsgi-docs.readthedocs.io/en/latest/Broodlord.html

    """
    def __init__(
            self, zerg_socket, zerg_die_on_idle=None, vassals_home=None,
            zerg_count=None, vassal_overload_sos_interval=None, vassal_queue_items_sos=None,
            section_emperor=None, section_zerg=None):
        """
        :param str|unicode zerg_socket: Unix socket to bind server to.

        :param int zerg_die_on_idle: A number of seconds after which an idle zerg will be destroyed.

        :param str|unicode|list[str|unicode] vassals_home: Set vassals home.

        :param int zerg_count: Maximum number of zergs to spawn.

        :param int vassal_overload_sos_interval: Ask emperor for reinforcement when overloaded.
            Accepts the number of seconds to wait between asking for a new reinforcements.

        :param int vassal_queue_items_sos: Ask emperor for sos if backlog queue has more
            items than the value specified
        """

        self.socket = zerg_socket
        self.vassals_home = vassals_home
        self.die_on_idle = zerg_die_on_idle
        self.broodlord_params = filter_locals(
            locals(), include=[
                'zerg_count',
                'vassal_overload_sos_interval',
                'vassal_queue_items_sos',
            ])

        section_emperor = section_emperor or Section()
        section_zerg = section_zerg or Section.derive_from(section_emperor)

        self.section_emperor = section_emperor
        self.section_zerg = section_zerg

    def configure(self):
        """Configures broodlord mode and returns emperor and zerg sections.

        :rtype: tuple
        """
        section_emperor = self.section_emperor
        section_zerg = self.section_zerg

        socket = self.socket

        section_emperor.workers.set_zerg_server_params(socket=socket)
        section_emperor.empire.set_emperor_params(vassals_home=self.vassals_home)
        section_emperor.empire.set_mode_broodlord_params(**self.broodlord_params)

        section_zerg.name = 'zerg'
        section_zerg.workers.set_zerg_client_params(server_sockets=socket)

        if self.die_on_idle:
            section_zerg.master_process.set_idle_params(timeout=30, exit=True)

        return section_emperor, section_zerg
