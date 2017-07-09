from collections import OrderedDict
from .utils import listify


if False:  # pragma: nocover
    from .config import Section
    from types import Union


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

        options_obj = section._options_objects.get(key)

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

    def __init__(self, *args, **kwargs):
        if self._section is None:
            self._section = kwargs.pop('_section')  # type: Section

        self.set_basic_params(*args, **kwargs)

    def set_basic_params(self, *args, **kwargs):
        return self._section

    def _make_key_val_string(self, locals_dict, keys=None, aliases=None, bool_keys=None, list_keys=None):
        value_chunks = []

        keys = keys or locals_dict.keys()
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

        return ','.join(value_chunks).strip()

    def _set(self, key, value, condition=True, cast=None, multi=False, on_top=False):

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

            if multi:
                values = opts.setdefault(key, [])

                if isinstance(value, list):
                    values.extend(value)
                else:
                    values.append(value)

            else:
                opts[key] = value


class SectionBase(OptionsGroup):

    def __init__(self, name='uwsgi', **kwargs):
        """

        :param str name: Configuration section name

        """
        self._section = self
        self._options_objects = OrderedDict()
        self._opts = OrderedDict()
        '''Main options container.'''

        super(SectionBase, self).__init__(**kwargs)

        self._set_basic_params_from_dict(kwargs)

        self.name = name

    def _set_basic_params_from_dict(self, src_dict):

        for key, value in src_dict.items():
            if not key.startswith('basic_params_') or not value:
                continue

            group_attr_name = key.replace('basic_params_', '')
            options_group = getattr(self, group_attr_name, None)  # type: Union[OptionsGroup, PluginBase]

            if options_group is not None:
                if 'plugin' in group_attr_name:
                    # Automatic plugin activation.
                    # Otherwise uWSGI in strict mode will complain
                    # about unknown options (from plugin).
                    options_group.activate(**value)

                else:
                    options_group.set_basic_params(**value)

    def __str__(self):
        return self.name

    def _get_options(self):
        options = []

        for name, val in self._section._opts.items():

            for val_ in listify(val):
                options.append((name, val_))

        return options


class PluginBase(OptionsGroup):
    """Plugin options."""

    name = None

    def __init__(self, *args, **kwargs):
        self._active = False
        super(PluginBase, self).__init__(*args, **kwargs)

    def set_basic_params(self, plugin_dir=None, **kwargs):
        """

        :param str|unicode plugin_dir: directory to search for plugin

        :param kwargs:
        """
        self._section.set_plugins_params(search_dirs=plugin_dir)

        return self._section

    def activate(self, **kwargs):
        """Activates the given plugin putting its definition into section."""

        if not self._active:
            # Prevent successive activations.
            self._section.set_plugins_params(plugins=self)
            self._active = True

        self.set_basic_params(**kwargs)

        return self._section

    def __str__(self):
        return self.name
