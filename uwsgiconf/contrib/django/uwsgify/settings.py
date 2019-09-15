from django.conf import settings


MODULE_INIT = getattr(settings, 'UWSGIFY_MODULE_INIT', 'uwsgiinit')
"""Name of a module with uWSGI runtime related stuff 
to automatically import from registered applications.

"""
