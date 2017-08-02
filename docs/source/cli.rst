Command-line interface (CLI)
============================

**uwsgiconf** comes with CLI (``click`` package required) to facilitate configuration.


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
