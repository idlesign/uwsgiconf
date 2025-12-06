# Advanced configuration

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
