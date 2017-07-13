

def format_print_text(text, color_fg=None, color_bg=None):
    """Format given text using ANSI formatting escape sequences.

    Could be useful gfor print command.

    :param str|unicode text:
    :param str|unicode color_fg: text (foreground) color
    :param str|unicode color_bg: text (background) color
    :rtype: str|unicode
    """
    from .config import Section

    color_fg = {

        'black': '30',
        'red': '31',
        'reder': '91',
        'green': '32',
        'greener': '92',
        'yellow': '33',
        'yellower': '93',
        'blue': '34',
        'bluer': '94',
        'magenta': '35',
        'magenter': '95',
        'cyan': '36',
        'cyaner': '96',
        'gray': '37',
        'grayer': '90',
        'white': '97',

    }.get(color_fg, '39')

    color_bg = {

        'black': '40',
        'red': '41',
        'reder': '101',
        'green': '42',
        'greener': '102',
        'yellow': '43',
        'yellower': '103',
        'blue': '44',
        'bluer': '104',
        'magenta': '45',
        'magenter': '105',
        'cyan': '46',
        'cyaner': '106',
        'gray': '47',
        'grayer': '100',
        'white': '107',

    }.get(color_bg, '49')

    mod = ';'.join([color_fg, color_bg])

    text = '%(esc)s[%(mod)sm%(value)s%(end)s' % {
        'esc': Section.vars.FORMAT_ESCAPE,
        'end': Section.vars.FORMAT_END,
        'mod': mod,
        'value': text,
    }

    return text


class FormatterBase(object):
    """Base class for configuration formatters."""

    def __init__(self, sections):
        self.sections = sections

    def iter_options(self):
        """Iterates configuration sections groups options."""
        for section in self.sections:
            name = str(section)
            for key, value in section._get_options():
                yield name, key, value

    def format(self):
        raise NotImplementedError()  # pragma: nocover


class IniFormatter(FormatterBase):
    """Translates a configuration as INI file."""

    def format(self):
        lines = []
        last_section = ''

        for section_name, key, value in self.iter_options():

            if section_name != last_section:
                lines.append('\n[%s]' % section_name)
                last_section = section_name

            lines.append('%s = %s' % (key, str(value).strip()))

        lines = '\n'.join(lines)
        return lines
