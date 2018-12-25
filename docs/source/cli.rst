Command-line interface (CLI)
============================

**uwsgiconf** comes with CLI (``click`` package required) to facilitate configuration.

.. code-block:: bash

    ; To install uwsgiconf with click:
    $ pip install uwsgiconf[cli]


Compile
-------

Compiles classic uWSGI configuration from a given `uwsgiconf` configuration module
(or from the default one - ``uwsgicfg.py``).

.. note:: Be sure that your configuration module defines ``configuration`` attribute.
  It mush hold one or more ``Configuration`` or ``Section`` (those will be automatically
  casted to configurations) objects. Callable as attribute value is supported.

.. code-block:: bash

    ; This compiles uwsgicfg.py from the current directory
    ; into .ini and prints that out:
    $ uwsgiconf compile

    ; This compiles there/thisfile.py file:
    $ uwsgiconf compile there/thisfile.py

    ; Add "> target_file.ini" to redirect output (configuration) into a file.


Run
---

Runs uWSGI using configuration from a given `uwsgiconf` configuration module
(or from the default one - ``uwsgicfg.py``).

.. note:: uWSGI process will replace ``uwsgiconf`` process.

.. code-block:: bash

    ; This runs uWSGI using uwsgicfg.py from the current directory.
    $ uwsgiconf run

    ; This runs uWSGI using configuration from there/thisfile.py:
    $ uwsgiconf run there/thisfile.py


Probe plugins
-------------

Shows available uWSGI plugins.

.. code-block:: bash

    $ uwsgiconf probe_plugins


Systemd and other configs
-------------------------

You can generate configuration files to launch ``uwsgiconf`` automatically using system facilities.

Config contents in sent to stdout and could be redirected into a file.

.. code-block:: bash

    $ uwsgiconf sysinit systemd
    $ uwsgiconf sysinit upstart


Usage example for Systemd:

.. code-block:: bash

    ; Generate and save config into `myapp.service` file
    $ uwsgiconf sysinit --project myapp > myapp.service

    ; Copy config into standard location
    $ sudo cp myapp.service /etc/systemd/system/

    ; Reload available configs information and run service
    $ sudo sh -c "systemctl daemon-reload; systemctl start myapp.service"

    ; Watch application log realtime (if syslog is used)
    $ journalctl -fu myapp.service

