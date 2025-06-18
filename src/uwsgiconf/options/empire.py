from ..base import OptionsGroup
from ..typehints import Strlist


class Empire(OptionsGroup):
    """Emperor and his vassals.

    If you need to deploy a big number of apps on a single server,
    or a group of servers, the Emperor mode is just the ticket.

    * http://uwsgi-docs.readthedocs.io/en/latest/Emperor.html

    """

    def set_emperor_params(
            self,
            *,
            vassals_home: Strlist = None,
            name: str | None = None,
            scan_interval: int | None = None,
            pid_file: str | None = None,
            spawn_asap: bool | None = None,
            stats_address: str | None = None,
            trigger_socket:str | None = None,
            links_no_follow: bool | None = None,
    ):
        """

        .. note:: The emperor should generally not be run with master, unless master features like advanced
            logging are specifically needed.

        .. note:: The emperor should generally be started at server boot time and left alone,
            not reloaded/restarted except for uWSGI upgrades;
            emperor reloads are a bit drastic, reloading all vassals at once.
            Instead vassals should be reloaded individually when needed, in the manner of the imperial monitor in use.

        :param vassals_home: Set vassals home and enable Emperor mode.

        :param name: Set the Emperor process name.

        :param scan_interval: Set the Emperor scan frequency. Default: 3 seconds.

        :param pid_file: Write the Emperor pid in the specified file.

        :param spawn_asap: Spawn the Emperor as soon as possible.

        :param stats_address: Run the Emperor stats server on specified address.

        :param trigger_socket: Enable the Emperor trigger socket.

        :param links_no_follow: Do not follow symlinks when checking for mtime.

        """
        self._set('emperor', vassals_home, multi=True)
        self._set('emperor-procname', name)
        self._set('emperor-freq', scan_interval)
        self._set('emperor-pidfile', pid_file)
        self._set('early-emperor', spawn_asap, cast=bool)
        self._set('emperor-stats-server', stats_address)
        self._set('emperor-trigger-socket', trigger_socket)
        self._set('emperor-nofollow', links_no_follow, cast=bool)

        return self._section

    def print_monitors(self):
        """Print out enabled imperial monitors."""

        self._set('imperial-monitor-list', value=True, cast=bool)

        return self._section

    def set_emperor_command_params(
            self,
            command_socket: str | None = None,
            *,
            wait_for_command: bool | None = None,
            wait_for_command_exclude: Strlist = None
    ):
        """Emperor commands related parameters.

        * http://uwsgi-docs.readthedocs.io/en/latest/tutorials/EmperorSubscriptions.html

        :param command_socket: Enable the Emperor command socket.
            It is a channel allowing external process to govern vassals.

        :param wait_for_command: Always wait for a 'spawn' Emperor command before starting a vassal.

        :param wait_for_command_exclude: Vassals that will ignore ``wait_for_command``.

        """
        self._set('emperor-command-socket', command_socket)
        self._set('emperor-wait-for-command', wait_for_command, cast=bool)
        self._set('emperor-wait-for-command-ignore', wait_for_command_exclude, multi=True)

        return self._section

    def set_vassals_wrapper_params(
            self,
            *,
            wrapper: str | None = None,
            overrides: Strlist = None,
            fallbacks: Strlist = None
    ):
        """Binary wrapper for vassals parameters.

        :param wrapper: Set a binary wrapper for vassals.

        :param overrides: Set a binary wrapper for vassals to try before the default one

        :param fallbacks: Set a binary wrapper for vassals to try as a last resort.
            Allows you to specify an alternative binary to execute when running a vassal
            and the default binary_path is not found (or returns an error).

        """
        self._set('emperor-wrapper', wrapper)
        self._set('emperor-wrapper-override', overrides, multi=True)
        self._set('emperor-wrapper-fallback', fallbacks, multi=True)

        return self._section

    def set_throttle_params(self, *, level: int | None = None, level_max: int | None = None):
        """Throttling options.

        * http://uwsgi-docs.readthedocs.io/en/latest/Emperor.html#throttling
        * http://uwsgi-docs.readthedocs.io/en/latest/Emperor.html#loyalty

        :param level: Set throttling level (in milliseconds) for bad behaving vassals. Default: 1000.

        :param level_max: Set maximum throttling level (in milliseconds)
            for bad behaving vassals. Default: 3 minutes.

        """
        self._set('emperor-throttle', level)
        self._set('emperor-max-throttle', level_max)

        return self._section

    def set_tolerance_params(self, *, for_heartbeat: int | None = None, for_cursed_vassals: int | None = None):
        """Various tolerance options.

        :param for_heartbeat: Set the Emperor tolerance about heartbeats.

            * http://uwsgi-docs.readthedocs.io/en/latest/Emperor.html#heartbeat-system

        :param for_cursed_vassals: Set the Emperor tolerance about cursed vassals.

            * http://uwsgi-docs.readthedocs.io/en/latest/Emperor.html#blacklist-system

        """
        self._set('emperor-required-heartbeat', for_heartbeat)
        self._set('emperor-curse-tolerance', for_cursed_vassals)

        return self._section

    def set_mode_tyrant_params(
            self,
            *,
            enable: bool | None = None,
            links_no_follow: bool | None = None,
            use_initgroups: bool | None = None
    ):
        """Tyrant mode (secure multi-user hosting).

        In Tyrant mode the Emperor will run the vassal using the UID/GID of the vassal
        configuration file.

        * http://uwsgi-docs.readthedocs.io/en/latest/Emperor.html#tyrant-mode-secure-multi-user-hosting

        :param enable: Puts the Emperor in Tyrant mode.

        :param links_no_follow: Do not follow symlinks when checking for uid/gid in Tyrant mode.

        :param use_initgroups: Add additional groups set via initgroups() in Tyrant mode.

        """
        self._set('emperor-tyrant', enable, cast=bool)
        self._set('emperor-tyrant-nofollow', links_no_follow, cast=bool)
        self._set('emperor-tyrant-initgroups', use_initgroups, cast=bool)

        return self._section

    def set_mode_broodlord_params(
            self,
            zerg_count: int | None = None,
            *,
            vassal_overload_sos_interval: int | None = None,
            vassal_queue_items_sos: int | None = None
    ):
        """This mode is a way for a vassal to ask for reinforcements to the Emperor.

        Reinforcements are new vassals spawned on demand generally bound on the same socket.

        .. warning:: If you are looking for a way to dynamically adapt the number
            of workers of an instance, check the Cheaper subsystem - adaptive process spawning mode.

            *Broodlord mode is for spawning totally new instances.*

        :param zerg_count: Maximum number of zergs to spawn.

        :param vassal_overload_sos_interval: Ask emperor for reinforcement when overloaded.
            Accepts the number of seconds to wait between asking for a new reinforcements.

        :param vassal_queue_items_sos: Ask emperor for sos if listen queue (backlog) has more
            items than the value specified

        """
        self._set('emperor-broodlord', zerg_count)
        self._set('vassal-sos', vassal_overload_sos_interval)
        self._set('vassal-sos-backlog', vassal_queue_items_sos)

        return self._section
