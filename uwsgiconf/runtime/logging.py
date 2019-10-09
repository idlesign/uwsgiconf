from .. import uwsgi


variable_set = uwsgi.set_logvar
"""Sets log variable.

:param str|unicode name:

:param str|unicode value:

:rtype: None
"""

variable_get = uwsgi.get_logvar
"""Return user-defined log variable contents.

* http://uwsgi.readthedocs.io/en/latest/LogFormat.html#user-defined-logvars

.. warning:: Bytes are returned for Python 3.

:param str|unicode name:

:rtype: bytes|str
"""

log_message = uwsgi.log
"""Logs a message.

:param str|unicode message:

:rtype: bool
"""

get_current_log_size = uwsgi.logsize
"""Returns current log size.

:rtype: long
"""