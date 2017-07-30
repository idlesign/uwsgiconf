from ..base import ParametrizedValue
from ..utils import listify


class HookAction(ParametrizedValue):

    pass


class ActionMount(HookAction):
    """Mount or unmount filesystems.

    Examples:
        * Mount: proc none /proc
        * Unmount: /proc

    """

    name = 'mount'

    def __init__(self, mountpoint, fs=None, src=None, flags=None):
        """

        :param str|unicode mountpoint:

        :param str|unicode fs: Filesystem. Presence indicates mounting.

        :param str|unicode src: Presence indicates mounting.

        :param str|unicode|list flags: Flags available for the operating system.
            As an example on Linux you will options like: bind, recursive, readonly, rec, detach etc.

        """
        if flags is not None:
            flags = listify(flags)
            flags = ','.join(flags)

        if fs:
            args = [fs, src, mountpoint, flags]

        else:
            args = [mountpoint, flags]
            self.name = 'umount'

        super(ActionMount, self).__init__(*args)


class ActionExecute(HookAction):
    """Run the shell command.

    Command run under ``/bin/sh``.
    If for some reason you do not want to use ``/bin/sh``,
    use ``binsh`` option,

    Examples:
        * cat /proc/self/mounts

    """

    name = 'exec'

    # todo consider adding safeexec
    def __init__(self, command):
        super(ActionExecute, self).__init__(command)


class ActionCall(HookAction):
    """Call functions in the current process address space."""

    name = 'call'

    def __init__(self, target, honour_exit_status=False, arg_int=False):
        """
        :param str|unicode target: Symbol and args.

        :param bool honour_exit_status: Expect an int return.
            Anything != 0 means failure.

        :param bool arg_int: Parse the argument as an int.

        """
        name = self.name

        if arg_int:
            name += 'int'

        if honour_exit_status:
            name += 'ret'

        self.name = name

        super(ActionCall, self).__init__(target)


class ActionDirChange(HookAction):
    """Changes a directory.

    Convenience action, same as ``call:chdir <directory>``.

    """
    name = 'cd'

    def __init__(self, target_dir):
        super(ActionDirChange, self).__init__(target_dir)


class ActionDirCreate(HookAction):
    """Creates a directory with 0777."""

    name = 'mkdir'

    def __init__(self, target_dir):
        super(ActionDirCreate, self).__init__(target_dir)


class ActionFileCreate(HookAction):
    """Creates a directory with 0666."""

    name = 'create'

    def __init__(self, fpath):
        super(ActionFileCreate, self).__init__(fpath)


class ActionExit(HookAction):
    """Exits.

    Convenience action, same as ``callint:exit [num]``.

    """
    name = 'exit'

    def __init__(self, status_code=None):
        super(ActionExit, self).__init__(status_code)


class ActionPrintout(HookAction):
    """Prints.

    Convenience action, same as calling the ``uwsgi_log`` symbol.

    """
    name = 'print'

    def __init__(self, text=None):
        super(ActionPrintout, self).__init__(text)


class ActionSetHostName(HookAction):
    """Sets a host name."""

    name = 'hostname'

    def __init__(self, name):
        super(ActionSetHostName, self).__init__(name)


class ActionAlarm(HookAction):
    """Issues an alarm. See ``.alarms`` options group."""

    name = 'alarm'

    def __init__(self, alarm, message):
        super(ActionAlarm, self).__init__(alarm, message)


class ActionFileWrite(HookAction):
    """Writes a string to the specified file.

    If file doesn't exist it will be created.

    .. note:: Since 1.9.21

    """
    name = 'write'

    def __init__(self, target, text, append=False, newline=False):
        """

        :param str|unicode target: File to write to.

        :param str|unicode text: Text to write into file.

        :param bool append: Append text instead of rewrite.

        :param bool newline: Add a newline at the end.

        """
        if append:
            self.name = 'append'

        if newline:
            self.name += 'n'

        super(ActionFileWrite, self).__init__(target, text)


class ActionFifoWrite(HookAction):
    """Writes a string to the specified FIFO (see ``fifo_file`` from ``master_process`` params)."""

    name = 'writefifo'

    def __init__(self, target, text, wait=False):
        """
        :param bool wait: Wait until FIFO is available.

        """
        if wait:
            self.name = 'spinningfifo'

        super(ActionFifoWrite, self).__init__(target, text)


class ActionUnlink(HookAction):
    """Unlink the specified file.

    .. note:: Since 1.9.21

    """
    name = 'unlink'

    def __init__(self, target):
        super(ActionUnlink, self).__init__(target)
