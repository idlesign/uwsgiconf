from collections import OrderedDict
from .utils import listify


if False:  # pragma: nocover
    from .config import Section


class Options(object):
    """Options descriptor. Allows option."""

    def __init__(self, opt_type):
        """
        :param opt_type:
        """
        self.opt_type = opt_type

    def __get__(self, section, section_cls):
        """

        :param Section section:
        :param OptionsGroup options_obj:
        :rtype: OptionsGroup
        """
        key = self.opt_type.__name__

        try:
            options_obj = section._options_objects.get(key)

        except AttributeError:
            # Allow easy access to option group static params:
            # Section.networking.socket_types.DEFAULT
            return self.opt_type

        if not options_obj:
            options_obj = self.opt_type(_section=section)

        section._options_objects[key] = options_obj

        return options_obj


class OptionsGroup(object):
    """Introduces group of options.

    Basic group parameters may be passed to initializer
    or `set_basic_params` method.

    Usually methods setting parameters are named `set_***_params`.

    Methods ending with `_params` return section object and may be chained.

    """
    _section = None  # type: Section
    """Section this option group belongs to."""

    plugin = False  # type: bool|str|unicode
    """Indication this option group belongs to a plugin."""

    name = None
    """Name to represent the group."""

    def __init__(self, *args, **kwargs):
        if self._section is None:
            self._section = kwargs.pop('_section', None)  # type: Section

        self.set_basic_params(*args, **kwargs)

    def _get_name(self, *args, **kwargs):
        """
        :rtype: str
        """
        return self.name

    def __str__(self):
        return self._get_name()

    def __call__(self, *args, **kwargs):
        """The call is translated into ``set_basic_params``` call.

        This approach is much more convenient yet IDE most probably won't
        give you a hint on what arguments are accepted.

        :param args:
        :param kwargs:
        :rtype: Section
        """
        return self.set_basic_params(*args, **kwargs)

    def set_basic_params(self, *args, **kwargs):
        """
        :rtype: Section
        """
        return self._section

    def _set(self, key, value, condition=True, cast=None, multi=False):

        def handle_plugin_required(val):

            if isinstance(val, ParametrizedValue):
                if val.plugin:
                    # Automatic plugin activation.
                    self._section.set_plugins_params(plugins=val.plugin)

                if val._opts:
                    opts.update(val._opts)

        if condition is True:
            condition = value is not None

        if condition is None or condition:

            opts = self._section._opts

            if cast is bool:
                if value:
                    value = 'true'

                else:
                    try:
                        del opts[key]
                    except KeyError:
                        pass

                    return

            if self.plugin is True:
                # Automatic plugin activation when option from it is used.
                self._section.set_plugins_params(plugins=[self])

            if multi:
                values = []

                # First activate plugin if required.
                for value in listify(value):
                    handle_plugin_required(value)
                    values.append(value)

                # Second: list in new option.
                opts.setdefault(key, []).extend(values)

            else:
                handle_plugin_required(value)
                opts[key] = value


class ParametrizedValue(OptionsGroup):
    """Represents parametrized option value."""

    alias = None
    args_joiner = ' '
    name_separator = ':'
    name_separator_strip = False

    def __init__(self, *args):
        self.args = args
        self._opts = OrderedDict()
        super(ParametrizedValue, self).__init__(_section=self)

    def __str__(self):
        args = [str(arg) for arg in self.args if arg is not None]

        result = self._get_name() + self.name_separator

        result += self.args_joiner.join(args)

        if self.alias:
            result = '%s %s' % (self.alias, result)

        result = result.strip()

        if self.name_separator_strip:
            result = result.strip(self.name_separator)

        return result
