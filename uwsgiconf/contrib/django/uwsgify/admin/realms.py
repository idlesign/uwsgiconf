from collections import OrderedDict

from django.utils.translation import gettext_lazy as _

from uwsgiconf.runtime.environ import uwsgi_env
from .base import OnePageAdmin


class SummaryAdmin(OnePageAdmin):

    def contribute_onepage_context(self, request, context):
        context.update({
            'info': OrderedDict([
                (_('Version'), uwsgi_env.get_version()),
                (_('Hostname'), uwsgi_env.hostname),
                (_('Started'), uwsgi_env.started_on),
                (_('Cores'), uwsgi_env.cores_count),
                (_('Workers'), uwsgi_env.workers_count),
                (_('Buffer'), uwsgi_env.buffer_size),
                (_('Clock'), uwsgi_env.clock),
                (_('Master PID'), uwsgi_env.master_pid),
                (_('Memory'), uwsgi_env.memory),
                (_('Threads support'), uwsgi_env.threads_enabled),
                (_('Current worker'), uwsgi_env.worker_id),
                (_('Requests served'), uwsgi_env.request.total_count),
            ]),
        })


class ConfigurationAdmin(OnePageAdmin):

    def contribute_onepage_context(self, request, context):
        context.update({
            'info': uwsgi_env.config,
        })
