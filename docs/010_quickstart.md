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

Let's make `uwsgicfg.py`. There we configure uWSGI using nice
`PythonSection` preset to run our web app (from `/home/idle/myapp/wsgi.py`).

```python
from uwsgiconf.config import configure_uwsgi
from uwsgiconf.presets.nice import PythonSection


def get_configurations():
    return PythonSection.bootstrap('http://127.0.0.1:8000', wsgi_module='/home/idle/myapp/wsgi.py')


configure_uwsgi(get_configurations)
```

Now we are ready to use this configuration:

```shell
; compile our configuration to into myconf.ini
uwsgiconf compile > myconf.ini

; run it using uWSGI as usual:
uwsgi myconf.ini

; or run in with uwsgiconf instead:
uwsgiconf run
```

## More details

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

## Configuration with multiple sections

Let's configure uWSGI to use Emperor Broodlord mode as described
[here](http://uwsgi-docs.readthedocs.io/en/latest/Broodlord.html#a-simple-example)
using `Broodlord` preset.

```python
from uwsgiconf.config import Section, Configuration
from uwsgiconf.presets.empire import Broodlord

emperor, zerg = Broodlord(

    zerg_socket='/tmp/broodlord.sock',
    zerg_count=40,
    zerg_die_on_idle=30,

    vassals_home='/etc/vassals',
    vassal_queue_items_sos=10,

    # We'll use the same basic params both for Broodlord Emperor and his zergs.
    section_emperor=(Section().
        # NOTE. Here we use a shortcut for ``set_basic_params`` methods:
        # E.g.: instead of `master_process.set_basic_params(enable=True)`
        # you say `master_process(enable=True)`.
        # But in that case you won't get any arg hints from you IDE.
        master_process(enable=True).
        workers(count=1).
        logging(no_requests=True).
        python.set_wsgi_params(module='werkzeug.testapp:test_app')
    ),

).configure()

# Bind Emperor to socket.
emperor.networking.register_socket(Section.networking.sockets.default(':3031'))

# Put Emperor and zerg sections into configuration.
multisection_config = Configuration([emperor, zerg])
```
