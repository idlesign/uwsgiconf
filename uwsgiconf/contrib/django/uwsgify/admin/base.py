from django.conf.urls import re_path
from django.contrib import admin
from django.template.response import TemplateResponse


class OnePageAdmin(admin.ModelAdmin):

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.model_name

        urlpatterns = [
            re_path('^$', self.admin_site.admin_view(self.view_onepage), name=f'%s_%s_changelist' % info)
        ]

        return urlpatterns

    def view_onepage(self, request):

        # Not on the top to protect from module caching
        # caused by 1. import from manage command 2. from uWSGI
        from uwsgiconf import uwsgi

        context = dict(
            self.admin_site.each_context(request),

            stub=uwsgi.is_stub,
            title=self.opts.verbose_name,
            model_meta=self.model._meta,
        )
        self.contribute_onepage_context(request, context)
        return TemplateResponse(request, 'admin/uwsgify/onepage.html', context)

    def contribute_onepage_context(self, request, context):
        raise NotImplementedError
