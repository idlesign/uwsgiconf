# Platform

Platform object is available in `uwsgi` module attribute:

```python
from uwsgiconf.runtime.platform import uwsgi

rss, vsz = uwsgi.memory

print(uwsgi.config)

@uwsgi.postfork_hooks.add()
def db_close_connections():
    """This will be called after fork()."""
    print('Forked!')
```

::: apidescribed: uwsgiconf.runtime.platform._Platform

::: apidescribed: uwsgiconf.runtime.request._Request
