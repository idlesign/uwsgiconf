

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
