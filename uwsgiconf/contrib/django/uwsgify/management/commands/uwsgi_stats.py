from ._base import ControlCommand


class Command(ControlCommand):

    help = 'Dump uWSGI configuration and current stats into the log'

    def get_cmd(self, options):
        return b's'
