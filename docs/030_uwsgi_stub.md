# Python uwsgi module stub

**uwsgiconf** comes with documented **uwsgi** module that you can import
instead of `import uwsgi`.

```python
# Instead of
import uwsgi

# you can do.
from uwsgiconf import uwsgi
```

That way **uwsgi** will be available runtime as usual, besides you will
get autocompletion and hints in IDE, and won't get `ImportError` when
run without **uwsgi**.

This also will facilitate your testing a bit, for those simple cases
when you won't expect any result from **uwsgi** function.

!!! tip
    This is a stub module, so it doesn't fully implement functions defined
    in it. Yet it tries to emulate uWSGI to some extent to facilitate testing.
    Use it for testing and documentation purposes.


## uwsgi.is_stub

You can check runtime whether you're using a stub:

```python
from uwsgiconf import uwsgi

if uwsgi.is_stub:
    ...
```

## Forcing stub

Sometimes (e.g. for tests but when uWSGI module is available) you may want to force stub.

That could be done with the help of `UWSGICONF_FORCE_STUB` environment variable:

```python
import os
os.environ['UWSGICONF_FORCE_STUB'] = '1'
```

---

::: apidescribed: uwsgiconf.uwsgi_stub
