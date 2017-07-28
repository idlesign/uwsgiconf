from __future__ import unicode_literals
from collections import namedtuple


EmbeddedPlugins = namedtuple('EmbeddedPlugins', ['generic', 'request'])


def listify(src):
    """Make a list with source object if not already a list.

    :param src:
    :rtype: list

    """
    if not isinstance(src, list):
        src = [src]

    return src


def filter_locals(locals_dict, drop=None):
    """Filters a dictionary produced by locals().

    :param dict locals_dict:

    :param list drop: Keys to drop from dict.

    :rtype: dict
    """
    drop = drop or []
    drop.extend([
        'self',
        '__class__',  # py3
    ])
    locals_dict = {k: v for k, v in locals_dict.items() if k not in drop}
    return locals_dict


def make_key_val_string(
        locals_dict, keys=None, aliases=None, bool_keys=None, list_keys=None,
        items_separator=','):
    """Flattens the given dictionary into key-value string.

    :param dict locals_dict: Dictionary produced by locals().

    :param list keys: Relevant keys from dictionary.
        If not defined - all keys are relevant.
        If defined keys will flattened into string using given order.

    :param dict aliases: Mapping key names from locals_dict into names
        they should be replaced with.

    :param list bool_keys: Keys to consider their values bool.

    :param list list_keys: Keys expecting lists.

    :param str|unicode items_separator: String to use as items (chunks) separator.

    :rtype: str|unicode
    """
    value_chunks = []

    keys = keys or sorted(filter_locals(locals_dict).keys())
    aliases = aliases or {}
    bool_keys = bool_keys or []
    list_keys = list_keys or []

    for key in keys:
        val = locals_dict[key]

        if val is not None:

            if key in bool_keys:
                val = 1

            elif key in list_keys:

                val = ';'.join(listify(val))

            value_chunks.append('%s=%s' % (aliases.get(key, key), val))

    return items_separator.join(value_chunks).strip()


class UwsgiRunner(object):
    """Exposes methods to run uWSGI."""

    def __init__(self, binary_path=None):
        self.binary_path = binary_path or 'uwsgi'

    def get_output(self, command_args):
        """Runs a command and returns its output (stdout + stderr).

        :param str|unicode|list[str|unicode] command_args:

        :rtype: str|unicode

        """
        from subprocess import Popen, STDOUT, PIPE

        command = [self.binary_path]
        command.extend(listify(command_args))

        process = Popen(command, stdout=PIPE, stderr=STDOUT)
        out, _ = process.communicate()

        return out

    def get_plugins(self):
        """Returns ``EmbeddedPlugins`` object with

        :rtype EmbeddedPlugins:
        """
        out = self.get_output('--plugin-list')
        return parse_command_plugins_output(out)


def parse_command_plugins_output(out):
    """Parses ``plugin-list`` command output from uWSGI
    and returns object containing lists of embedded plugin names.

    :param str|unicode out:

    :rtype EmbeddedPlugins:

    """
    out = out.split('--- end of plugins list ---')[0]
    out = out.partition('plugins ***')[2]
    out = out.splitlines()

    current_slot = 0

    plugins = EmbeddedPlugins([], [])

    for line in out:
        line = line.strip()

        if not line:
            continue

        if line.startswith('***'):
            current_slot += 1
            continue

        if current_slot is not None:
            plugins[current_slot].append(line)

    plugins = plugins._replace(request=[plugin.partition(' ')[2] for plugin in plugins.request])

    return plugins
