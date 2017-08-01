
class Var(object):

    tpl = '%s'

    def __init__(self, name):
        self._name = name

    def __str__(self):
        return self.tpl % self._name


class Func(Var):

    pass


class VarRequest(Var):
    """Returns request variable. Examples: PATH_INFO, SCRIPT_NAME, REQUEST_METHOD."""
    tpl = '${%s}'


class VarMetric(Var):
    """Returns metric (see ``monitoring``) variable."""
    tpl = '${metric[%s]}'


class VarCookie(Var):
    """Returns cookie variable"""
    tpl = '${cookie[%s]}'


class VarQuery(Var):
    """Returns query string variable."""
    tpl = '${qs[%s]}'


class VarUwsgi(Var):
    """Returns internal uWSGI information.

     Supported variables:
        * wid
        * pid
        * uuid
        * status

    """
    tpl = '${uwsgi[%s]}'


class VarTime(Var):
    """Returns time/date in various forms.

    Supported variables:
        * unix

    """
    tpl = '${time[%s]}'


class VarHttptime(Var):
    """Returns http date adding the numeric argument (if specified)
    to the current time (use empty arg for current server time).

    """
    tpl = '${httptime[%s]}'


class FuncMime(Func):
    """Returns mime type of a variable."""
    tpl = '${mime[%s]}'


class FuncMath(Func):
    """Perform a math operation. Example: CONTENT_LENGTH+1

    Supported operations: + - * /

    .. warning:: Requires matheval support.

    """
    tpl = '${math[%s]}'


class FuncBase64(Func):
    """Encodes the specified var in base64"""
    tpl = '${base64[%s]}'


class FuncHex(Func):
    """Encodes the specified var in hex."""
    tpl = '${hex[%s]}'


class FuncUpper(Func):
    """Uppercase the specified var."""
    tpl = '${upper[%s]}'


class FuncLower(Func):
    """Lowercase the specified var."""
    tpl = '${lower[%s]}'
