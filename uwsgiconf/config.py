import os
from datetime import datetime
from collections import OrderedDict
from functools import partial

from .base import SectionBase, PluginBase, Options
from .options import *
from .formatters import IniFormatter, format_print_text
from .exceptions import ConfigurationError
from .utils import listify


class Section(SectionBase):
    """Configuration section.

    Options within configuration section are gathered into groups such as:
        * applications
        * locks
        * main_process
        * master_process
        * networking
        * workers

    Options offered by plugins are prefixed with `plugin_`:

        * plugin_python

    Usually in group objects methods setting parameters are named `set_***_params`.
    Methods ending with `_params` usually return section object to allow chaining.

    You can pass options group basic parameters
    not only into `set_basic_params` method by also into section initializer
    using `basic_params_` prefixed group name:

        Section(
            basic_params_workers=dict(count=3, zombie_reaper=True)
            basic_params_master_process=dict(enabled=True)
        )

    """
    applications = Options(Applications)  # type: Applications
    caching = Options(Caching)  # type: Caching
    locks = Options(Locks)  # type: Locks
    main_process = Options(MainProcess)  # type: MainProcess
    master_process = Options(MasterProcess)  # type: MasterProcess
    networking = Options(Networking)  # type: Networking
    queue = Options(Queue)  # type: Queue
    spooler = Options(Spooler)  # type: Spooler
    workers = Options(Workers)  # type: Workers

    plugin_python = Options(PythonPlugin)  # type: PythonPlugin

    class Vars(object):
        """The following variables also known as magic variables could be used as option values where appropriate.

        * http://uwsgi-docs.readthedocs.io/en/latest/Configuration.html#magic-variables

        """
        VERSION = '%V'
        '''uWSGI version number'''

        FORMAT_ESCAPE = '%['
        '''ANSI escape \\033. useful for printing colors'''

        FORMAT_END = '%s[0m' % FORMAT_ESCAPE

        CONF_CURRENT_SECTION = '%x'
        '''The current section identifier, eg. conf.ini:section.'''
        CONF_CURRENT_SECTION_NTPL = '%x'

        CONF_NAME_ORIGINAL = '%o'
        '''The original conf filename, as specified on the command line'''
        CONF_NAME_ORIGINAL_NTPL = '%O'

        TIMESTAMP_STARTUP_S = '%t'
        '''Unix time s, gathered at instance startup.'''
        TIMESTAMP_STARTUP_MS = '%T'
        '''Unix time ms, gathered at instance startup'''

        DIR_VASSALS = '%v'
        '''Vassals directory - pwd.'''

        HOST_NAME = '%h'
        '''Host name.'''
        CPU_CORES = '%k'
        '''Detected CPU count.'''

        USER_ID = '%u'
        '''User ID.'''
        USER_NAME = '%U'
        '''User name.'''

        GROUP_ID = '%g'
        '''Use group ID.'''
        GROUP_NAME = '%G'
        '''Use group name.'''

        @classmethod
        def get_descriptions(cls):
            """Returns variable to description mapping.

            :rtype: dict
            """
            descriptions = {
                cls.DIR_VASSALS: 'the vassals directory - pwd',
                cls.VERSION: 'the uWSGI version',
                cls.HOST_NAME: 'the hostname',
                cls.CONF_NAME_ORIGINAL: 'the original conf filename, as specified on the command line',
                cls.CONF_NAME_ORIGINAL_NTPL: 'as %o but for first non-template conf',
                '%p': 'the absolute path of the conf',
                '%P': 'as %p but for first non-template conf',
                '%s': 'the filename of the conf',
                '%S': 'as %s but for first non-template conf',
                '%d': 'the absolute path of the directory containing the conf',
                '%D': 'as %d but for first non-template conf',
                '%e': 'the extension of the conf',
                '%E': 'as %e but for first non-template conf',
                '%n': 'the filename without extension',
                '%N': 'as %n but for first non-template conf',
                '%c': 'the name of the directory containing the conf file',
                '%C': 'as %c but for first non-template conf',
                cls.TIMESTAMP_STARTUP_S: 'unix time s, gathered at instance startup',
                cls.TIMESTAMP_STARTUP_MS: 'unix time ms, gathered at instance startup',
                cls.CONF_CURRENT_SECTION: 'the current section identifier, eg. conf.ini:section',
                '%X': 'as %x but for first non-template conf',
                '%i': 'inode number of the file',
                '%I': 'as %i but for first non-template conf',
                cls.FORMAT_ESCAPE: 'ANSI escape \\033. useful for printing colors',
                cls.CPU_CORES: 'detected cpu cores',
                cls.USER_ID: 'uid of the user',
                cls.USER_NAME: 'username or fallback to uid of the user',
                cls.GROUP_ID: 'gid of the user',
                cls.GROUP_NAME: 'group name or fallback to gid of the user',
                '%j': 'HEX representation of the djb33x hash of the full conf path',
                '%J': 'as %j but for first non-template conf',
            }

            descriptions = sorted(descriptions.items(), key=lambda item: item[0].lower())

            return OrderedDict(descriptions)

    def __init__(self, strict_config=None, name=None, **kwargs):
        """

        :param bool strict_config: Enable strict configuration parsing.
            If any unknown option is encountered in a configuration file,
            an error is shown and uWSGI quits.

            To use placeholder variables when using strict mode, use the ``set-placeholder`` option.

        :param str name: Configuration section name

        """
        super(Section, self).__init__(name=name or 'uwsgi', strict_config=strict_config, **kwargs)

    def set_basic_params(self, strict_config=None, **kwargs):

        self._set('strict', strict_config, cast=bool)

        return self

    def as_configuration(self):
        """Returns configuration object including only one (this very) section.

        :rtype: Configuration
        """
        return Configuration([self])

    def print_plugins(self):
        """Print out enabled plugins."""

        self._set('plugins-list', True, cast=bool)

        return self

    def print_stamp(self):
        """Prints out a stamp containing useful information,
        such as what and when has generated this configuration.

        """
        from . import VERSION

        print_out = partial(self.print_out, format_options='red')
        print_out('This configuration was automatically generated using')
        print_out('uwsgiconf v%s on %s' % ('.'.join(map(str, VERSION)), datetime.now().isoformat(' ')))

        return self

    def print_out(self, value, indent=None, format_options=None, immediate=False):
        """Prints out the given value.

        :param value:

        :param str|unicode indent:

        :param dict|str|unicode format_options: text color

        :param bool immediate: Print as soon as possible.

        """
        if indent is None:
            indent = '>   '

        text = indent + str(value)

        if format_options is None:
            format_options = 'gray'

        if format_options:

            if not isinstance(format_options, dict):
                format_options = {'color_fg': format_options}

            text = format_print_text(text, **format_options)

        command = 'iprint' if immediate else 'print'
        self._set(command, text, multi=True)

        return self

    def print_variables(self):
        """Prints out magic variables available in config files
        alongside with their values and descriptions.
        May be useful for debugging.

        http://uwsgi-docs.readthedocs.io/en/latest/Configuration.html#magic-variables

        """
        print_out = partial(self.print_out, format_options='green')

        print_out('===== variables =====')

        for var, hint in self.Vars.get_descriptions().items():
            print_out('    %' + var + ' = ' + var + ' = ' + hint.replace('%', '%%'))

        print_out('=====================')

        return self

    def set_plugins_params(self, plugins=None, search_dirs=None, autoload=None, required=False):
        """Sets plugin-related parameters.

        :param list|str|unicode|PluginBase|list[PluginBase] plugins: uWSGI plugins to load

        :param list|str|unicode search_dirs: Directories to search for uWSGI plugins.

        :param bool autoload: Try to automatically load plugins when unknown options are found.

        :param bool required: Load uWSGI plugins and exit on error.

        """
        plugins = plugins or []

        command = 'need-plugin' if required else 'plugin'

        for plugin in listify(plugins):
            self._set(command, plugin, multi=True)

        self._set('plugins-dir', search_dirs, multi=True)
        self._set('autoload', autoload, cast=bool)

        return self

    def set_fallback(self, target):
        """Sets a fallback configuration for section.

        Re-exec uWSGI with the specified config when exit code is 1.

        :param str|unicode|Section target: File path or Section to include.
        """
        if isinstance(target, Section):
            target = ':' + target.name

        self._set('fallback-config', target)

        return self

    def env(self, key, value=None, unset=False, immediate=False):
        """Processes (sets/unsets) environment variable.

        If is not given in `set` mode value will be taken from current env.

        :param str|unicode key:

        :param value:

        :param bool unset: Whether to unset this variable.

        :param bool immediate: If True env variable will be set as soon as possible.

        """
        if unset:
            self._set('unenv', key, multi=True)
        else:
            if value is None:
                value = os.environ.get(key)

            self._set('%senv' % ('i' if immediate else ''), '%s=%s' % (key, value), multi=True)

        return self

    def include(self, target):
        """Includes target contents into config.

        :param str|unicode|Section|list target: File path or Section to include.
        """
        for target_ in listify(target):
            if isinstance(target_, Section):
                target_ = ':' + target_.name

            self._set('ini', target_, multi=True)

        return self


class Configuration(object):
    """
    Configuration is comprised from one or more Sections and could
    be represented in format natively supported by uWSGI.

    """

    def __init__(self, sections=None, autoinclude_sections=True):
        """

        :param list[Section] sections: If not provided, empty section
            will be automatically generated.

        :param bool autoinclude_sections: Whether to include
            in the first sections all subsequent sections.

        """
        super(Configuration, self).__init__()

        sections = sections or [Section()]
        self._validate_sections(sections)

        if autoinclude_sections:

            first = sections[0]
            for section in sections[1:]:
                first.include(section)

        self.sections = sections

    @classmethod
    def _validate_sections(cls, sections):
        """Validates sections types and uniqueness."""
        names = []
        for section in sections:

            if not hasattr(section, 'name'):
                raise ConfigurationError('`sections` attribute requires a list of Section')

            name = section.name
            if name in names:
                raise ConfigurationError('`%s` section name must be unique' % name)

            names.append(name)

    def format(self, do_print=False, stamp=True):
        """Applies formatting to configuration.

        *Currently formats to .ini*

        :param bool do_print: Whether to print out formatted config.
        :param bool stamp: Whether to add stamp data to the first configuration section.
        :rtype: str|unicode
        """
        if stamp and self.sections:
            self.sections[0].print_stamp()

        formatted = IniFormatter(self.sections).format()

        if do_print:
            print(formatted)

        return formatted

    def print_ini(self):
        """Print out this configuration as .ini.

        :rtype: str|unicode
        """
        return self.format(do_print=True)
