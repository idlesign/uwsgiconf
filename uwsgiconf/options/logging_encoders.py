from ..base import ParametrizedValue


class Encoder(ParametrizedValue):

    name_separator = ' '


class EncoderPrefix(Encoder):
    """Add a raw prefix to each log msg."""

    name = 'prefix'

    def __init__(self, value):
        """

        :param str|unicode value: Value to be used as affix

        """
        super(EncoderPrefix, self).__init__(value)


class EncoderSuffix(EncoderPrefix):
    """Add a raw suffix to each log msg"""

    name = 'suffix'


class EncoderNewline(Encoder):
    """Add a newline char to each log msg."""

    name = 'nl'


class EncoderGzip(Encoder):
    """Compress each msg with gzip (requires zlib)."""

    name = 'gzip'


class EncoderCompress(Encoder):
    """Compress each msg with zlib compress (requires zlib)."""

    name = 'compress'


class EncoderFormat(Encoder):
    """Apply the specified format to each log msg."""

    name = 'format'

    def __init__(self, template):
        """

        :param str|unicode template: Template string.
            Available variables are listed in ``FormatEncoder.Vars``.

        """
        super(EncoderFormat, self).__init__(template)

    class vars(object):
        """Variables available to use."""

        MESSAGE = '${msg}'
        """Raw log message (newline stripped)."""

        MESSAGE_NEWLINE = '${msgnl}'
        """Raw log message (with newline)."""

        TIME = '${unix}'
        """Current unix time."""

        TIME_MS = '${micros}'
        """Current unix time in microseconds."""

        # todo consider adding ${strftime:xxx} - strftime using the xxx format


class EncoderJson(EncoderFormat):
    """Apply the specified format to each log msg with each variable json escaped."""

    name = 'json'
