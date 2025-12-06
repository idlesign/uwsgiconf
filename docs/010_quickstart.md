# Quickstart

## Install

You can get and install **uwsgiconf** from PyPI using `pip`:

```shell
pip install uwsgiconf
```

## CLI

**uwsgiconf** expects `click` package available for CLI but won't
install this dependency by default.

Use the following command to install **uwsgiconf** with `click`:

```shell
pip install uwsgiconf[cli]
```

## Running Python web application

### Static configuration

Static configuration is used to set up basic uWSGI parameters to start with. 

Let's make `uwsgicfg.py`. There we configure uWSGI using nice
`PythonSection` preset to run our web app (from `/home/idle/myapp/wsgi.py`).

```python
from uwsgiconf.config import configure_uwsgi
from uwsgiconf.presets.nice import PythonSection


def get_configurations():
    return PythonSection.bootstrap('http://127.0.0.1:8000', wsgi_module='/home/idle/myapp/wsgi.py', mules=1)


configure_uwsgi(get_configurations)
```

!!! tip
    Interesting static configuration examples are located in `demos` directory of the repository. 


### Dynamic configuration

Dynamic configuration is used to set up additional parameters after uWSGI is started. 

It can be done in `wsgi.py` (see above) or in any other file imported by your app.

```python
from uwsgiconf.runtime.mules import Mule
from uwsgiconf.runtime.scheduling import register_timer 

# Let's print 'tick' every second in background.
# Background processing is handled by mules (note `mules=1` in PythonSection.bootstrap() above).
@register_timer(1, target=Mule(1))
def timer_1():
    print('tick')

```

!!! note
    There is much more than just background processing. See `Runtime` documentation section.


### Running

Now we are ready to use this configuration:

```shell
; we can compile the configuration into myconf.ini
uwsgiconf compile > myconf.ini

; and run it using uWSGI as usual:
uwsgi myconf.ini

; or we can run uWSGI with our config directly with uwsgiconf:
uwsgiconf run
```

## Fine tune static configuration

Fine tune is also available. 

```python
from uwsgiconf.config import configure_uwsgi
from uwsgiconf.presets.nice import PythonSection


def get_configurations():
    """This should return one or more Section or Configuration objects.
    In such a way you can configure more than one uWSGI instance in the same place.

    """
    my_app_dir = '/home/idle/myapp/'

    section = PythonSection(
        # Reload uWSGI when this file is updated.
        touch_reload=__file__,

        params_python=dict(
            # Let's add something to Python path.
            search_path='/opt/apps_shared/',
        ),

        wsgi_module=f'{my_app_dir}wsgi.py',

        # We'll redirect logs into a file.
        log_into=f'{my_app_dir}app.log',

        # If your uWSGI has no basic plugins embedded
        # (i.e. not from PyPI) you can give uwsgiconf a hint:
        embedded_plugins=False,

    ).networking.register_socket(
        # Make our app available at all ipv6 interfaces on port 8030
        PythonSection.networking.sockets.http('[::]:8030')
    )

    return section

configure_uwsgi(get_configurations)
```
