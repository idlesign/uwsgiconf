from collections import OrderedDict
from datetime import datetime, timedelta

from django.template.defaultfilters import filesizeformat
from django.utils.translation import gettext_lazy as _

from .base import OnePageAdmin


class SummaryAdmin(OnePageAdmin):

    def contribute_onepage_context(self, request, context):
        from uwsgiconf.runtime.environ import uwsgi_env
        from uwsgiconf.runtime.logging import get_current_log_size
        from uwsgiconf.runtime.rpc import get_rpc_list
        from uwsgiconf.runtime.signals import get_available_num

        time_started = datetime.fromtimestamp(uwsgi_env.started_on)
        rss, vsz = uwsgi_env.memory

        info_basic = OrderedDict([
            (_('Version'), uwsgi_env.get_version()),
            (_('Hostname'), uwsgi_env.hostname),
            (_('Serving since'), time_started),
            (_('Serving for'), datetime.now() - time_started),
            (_('Clock'), uwsgi_env.clock),
            (_('Master PID'), uwsgi_env.master_pid),
            (_('Memory (RSS, VSZ)'), ', '.join((filesizeformat(rss), filesizeformat(vsz)))),
            (_('Buffer size'), uwsgi_env.buffer_size),
            (_('Cores'), uwsgi_env.cores_count),
            (_('Workers'), uwsgi_env.workers_count),
            (_('Threads support'), '+' if uwsgi_env.threads_enabled else '-'),
            (_('Current worker'), uwsgi_env.worker_id),
            (_('Requests by worker'), uwsgi_env.request.id),
            (_('Requests total'), uwsgi_env.request.total_count),
            (_('Socket queue size'), uwsgi_env.get_listen_queue()),
            (_('Log size'), get_current_log_size()),
            (_('RPC'), ', '.join(get_rpc_list())),
            (_('Available signal number'), get_available_num()),
        ])

        context.update({
            'panels': {
                '': {
                    'rows': OrderedDict(((key, [val]) for key, val in info_basic.items())),
                }
            },
        })


class ConfigurationAdmin(OnePageAdmin):

    def contribute_onepage_context(self, request, context):
        from uwsgiconf.runtime.environ import uwsgi_env

        context.update({
            'panels': {
                '': {'rows': OrderedDict(((key, [val]) for key, val in uwsgi_env.config.items()))},
            },
        })
