from __future__ import unicode_literals, absolute_import

import os
import sys
import logging
from collections import namedtuple
from contextlib import contextmanager
from importlib import import_module

try:  # pragma: nocover
    from StringIO import StringIO
except ImportError:  # pragma: nocover
    from io import StringIO

from .settings import CONFIGS_MODULE_ATTR, ENV_CONF_ALIAS


if False:  # pragma: nocover
    from uwsgiconf.config import Configuration


PY3 = sys.version_info[0] == 3

if PY3:  # pragma: nocover
    string_types = str,

else:  # pragma: nocover
    string_types = basestring,


EmbeddedPlugins = namedtuple('EmbeddedPlugins', ['generic', 'request'])


def get_logger(name):
    # Here to mitigate module name clashing.
    return logging.getLogger(name)


def encode(value):
    """Encodes str into bytes if required."""
    return value.encode('utf-8') if PY3 and isinstance(value, str) else value


def decode(value):
    """Decodes bytes into str if required."""
    return value.decode('utf-8') if PY3 and isinstance(value, bytes) else value


@contextmanager
def output_capturing():
    """Temporarily captures/redirects stdout."""
    out = sys.stdout

    sys.stdout = StringIO()

    try:
        yield

    finally:
        sys.stdout = out


class ConfModule(object):
    """Represents a uwsgiconf configuration module.

    Allows reading configurations from .py files.

    """
    default_name = 'uwsgicfg.py'

    def __init__(self, fpath):
        """Module filepath.

        :param fpath:
        """
        fpath = os.path.abspath(fpath)
        self.fpath = fpath
        self._confs = None

    def spawn_uwsgi(self, only=None):
        """Spawns uWSGI process(es) which will use configuration(s) from the module.

        Returns list of tuples:
            (configuration_alias, uwsgi_process_id)

        If only one configuration found current process (uwsgiconf) is replaced with a new one (uWSGI),
        otherwise a number of new detached processes is spawned.

        :param str|unicode only: Configuration alias to run from the module.
            If not set uWSGI will be spawned for every configuration found in the module.

        :rtype: list
        """
        spawned = []
        configs = self.configurations

        if len(configs) == 1:

            alias = configs[0].alias
            UwsgiRunner().spawn(self.fpath, alias, replace=True)
            spawned.append((alias, os.getpid()))

        else:
            for config in configs:  # type: Configuration
                alias = config.alias

                if only is None or alias == only:
                    pid = UwsgiRunner().spawn(self.fpath, alias)
                    spawned.append((alias, pid))

        return spawned

    @property
    def configurations(self):
        """Configurations from uwsgiconf module."""

        if self._confs is not None:
            return self._confs

        with output_capturing():
            module = self.load(self.fpath)
            confs = getattr(module, CONFIGS_MODULE_ATTR)
            confs = listify(confs)

        self._confs = confs

        return confs

    @classmethod
    def load(cls, fpath):
        """Loads a module and returns its object.

        :param str|unicode fpath:
        :rtype: module
        """
        module_name = os.path.splitext(os.path.basename(fpath))[0]

        sys.path.insert(0, os.path.dirname(fpath))
        try:
            module = import_module(module_name)

        finally:
            sys.path = sys.path[1:]

        return module


def listify(src):
    """Make a list with source object if not already a list.

    :param src:
    :rtype: list

    """
    if not isinstance(src, list):
        src = [src]

    return src


def filter_locals(locals_dict, drop=None, include=None):
    """Filters a dictionary produced by locals().

    :param dict locals_dict:

    :param list drop: Keys to drop from dict.

    :param list include: Keys to include into dict.

    :rtype: dict
    """
    drop = drop or []
    drop.extend([
        'self',
        '__class__',  # py3
    ])

    include = include or locals_dict.keys()

    relevant_keys = [key for key in include if key not in drop]

    locals_dict = {k: v for k, v in locals_dict.items() if k in relevant_keys}

    return locals_dict


class KeyValue(object):
    """Allows lazy flattening the given dictionary into a key-value string."""

    def __init__(
            self, locals_dict, keys=None, aliases=None, bool_keys=None, list_keys=None,
            items_separator=','):
        """
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
        self.locals_dict = dict(locals_dict)
        self.keys = keys or sorted(filter_locals(locals_dict).keys())
        self.aliases = aliases or {}
        self.bool_keys = bool_keys or []
        self.list_keys = list_keys or []
        self.items_separator = items_separator

    def __str__(self):
        value_chunks = []

        for key in self.keys:
            val = self.locals_dict[key]

            if val is not None:

                if key in self.bool_keys:
                    val = 1

                elif key in self.list_keys:

                    val = ';'.join(listify(val))

                value_chunks.append('%s=%s' % (self.aliases.get(key, key), val))

        return self.items_separator.join(value_chunks).strip()


class UwsgiRunner(object):
    """Exposes methods to run uWSGI."""

    def __init__(self, binary_path=None):
        self.binary_uwsgi = binary_path or 'uwsgi'
        self.binary_python = self.prepare_env()

    def get_output(self, command_args):
        """Runs a command and returns its output (stdout + stderr).

        :param str|unicode|list[str|unicode] command_args:

        :rtype: str|unicode

        """
        from subprocess import Popen, STDOUT, PIPE

        command = [self.binary_uwsgi]
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

    @classmethod
    def prepare_env(cls):
        """Prepares current environment and returns Python binary name.

        This adds some virtualenv friendliness so that we try use uwsgi from it.

        :rtype: str|unicode
        """
        python_binary = sys.executable
        basepath = os.path.dirname(python_binary)

        os.environ['PATH'] = basepath + os.pathsep + os.environ['PATH']

        return os.path.basename(python_binary)

    def spawn(self, filepath, configuration_alias, replace=False):
        """Spawns uWSGI using the given configuration module.

        :param str|unicode filepath:

        :param str|unicode configuration_alias:

        :param bool replace: Whether a new process should replace current one.

        """
        # Pass --conf as an argument to have a chance to use
        # touch reloading form .py configuration file change.
        args = ['uwsgi', '--ini', 'exec://%s %s --conf %s' % (self.binary_python, filepath, configuration_alias)]

        if replace:
            return os.execvp('uwsgi', args)

        return os.spawnvp(os.P_NOWAIT, 'uwsgi', args)


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


def get_uwsgi_stub_attrs_diff():
    """Returns attributes difference two elements tuple between
    real uwsgi module and its stub.

    Might be of use while describing in stub new uwsgi functions.

    :return: (uwsgi_only_attrs, stub_only_attrs)

    :rtype: tuple
    """

    try:
        import uwsgi

    except ImportError:
        from uwsgiconf.exceptions import UwsgiconfException

        raise UwsgiconfException(
            '`uwsgi` module is unavailable. Calling `get_attrs_diff` in such environment makes no sense.')

    from . import uwsgi_stub

    def get_attrs(src):
        return set(attr for attr in dir(src) if not attr.startswith('_'))

    attrs_uwsgi = get_attrs(uwsgi)
    attrs_stub = get_attrs(uwsgi_stub)

    from_uwsgi = sorted(attrs_uwsgi.difference(attrs_stub))
    from_stub = sorted(attrs_stub.difference(attrs_uwsgi))

    return from_uwsgi, from_stub
