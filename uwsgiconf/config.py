import os
from datetime import datetime
from functools import partial

from .base import SectionBase, PluginOptionsGroupBase, Options
from .options import *
from .formatters import IniFormatter, format_print_text
from .exceptions import ConfigurationError


class Section(SectionBase):
    """Configuration section.

    Options within configuration section are gathered into groups.
    Options groups attributes are prefixed with `grp_`.

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
    grp_networking = Options(Networking)  # type: Networking
    grp_workers = Options(Workers)  # type: Workers
    grp_master_process = Options(MasterProcess)  # type: MasterProcess
    grp_main_process = Options(MainProcess)  # type: MainProcess
    grp_locks = Options(Locks)  # type: Locks

    grp_plugin_python = Options(PythonPlugin)  # type: PythonPlugin

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

    def add_stamp(self):
        """Adds a stamp containing useful information,
        such as what and when has generated this configuration.

        """
        from . import VERSION

        print_out = partial(self.print_out, format_options='red')
        print_out('This configuration was automatically generated using')
        print_out('uwsgiconf v%s on %s' % ('.'.join(map(str, VERSION)), datetime.now().isoformat(' ')))

        return self

    def print_out(self, value, indent=None, format_options=None):
        """Prints out the given value.

        :param value:
        :param str|unicode indent:
        :param dict|str|unicode format_options: text color
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

        self._set('print', text, multi=True)

        return self

    def print_variables(self):
        """Prints out magic variables available in config files
        alongside with their values and descriptions.
        May be useful for debugging.

        http://uwsgi-docs.readthedocs.io/en/latest/Configuration.html#magic-variables

        """
        from .variables import get_descriptions

        print_out = partial(self.print_out, format_options='green')

        print_out('===== variables =====')

        for var, hint in get_descriptions().items():
            print_out('    %' + var + ' = ' + var + ' = ' + hint.replace('%', '%%'))

        print_out('=====================')

        return self

    def set_plugins_params(self, plugins=None, search_dirs=None, autoload=None):
        """Sets plugin-related parameters.

        :param list|str|unicode|PluginOptionsGroupBase plugins: uWSGI plugins to load

        :param list|str|unicode search_dirs: directories to search for uWSGI plugins

        :param bool autoload: try to automatically load plugins when unknown options are found

        """
        plugins = plugins or []

        if not isinstance(plugins, list):
            plugins = [plugins]

        for plugin in plugins:
            self._set('plugin', plugin, multi=True)

        self._set('plugins-dir', search_dirs, multi=True)
        self._set('autoload', autoload, cast=bool)

        return self

    def set_fallback(self, target):
        """Sets a fallback configuration for section.

        :param str|unicode|Section target: File path or Section to include.
        """
        if isinstance(target, Section):
            target = ':' + target.name

        self._set('fallback-config', target)

        return self

    def env(self, key, value=None, unset=False):
        """Processes (sets/unsets) environment variable.

        If is not given in `set` mode value will be taken from current env.

        :param str|unicode key:
        :param value:
        :param bool unset:
        """
        if unset:
            self._set('unenv', key, multi=True)
        else:
            if value is None:
                value = os.environ.get(key)

            self._set('env', '%s=%s' % (key, value), multi=True)

        return self

    def include(self, target):
        """Includes target contents into config.

        :param str|unicode|Section|list target: File path or Section to include.
        """
        if not isinstance(target, list):
            target = [target]

        for target_ in target:
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
            self.sections[0].add_stamp()

        formatted = IniFormatter(self.sections).format()

        if do_print:
            print(formatted)

        return formatted

    def print_ini(self):
        """Print out this configuration as .ini.

        :rtype: str|unicode
        """
        return self.format(do_print=True)
