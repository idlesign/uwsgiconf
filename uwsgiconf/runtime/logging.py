from .. import uwsgi


variable_set = uwsgi.set_logvar

variable_get = uwsgi.get_logvar

log_message = uwsgi.log

get_current_log_size = uwsgi.logsize
