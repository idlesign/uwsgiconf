Quickstart
==========

Strategies
----------

Two main strategies to use **uwsgiconf**:

1. **Static:** create configuration .py and compile in on demand into classic uWSGI .ini.
2. **Dynamic:** create configuration .py, make it executable and give it directly to uWSGI

  .. code-block:: bash

    uwsgi --ini 'exec://path/to/myconf.py'


Using a preset to run Python web application
--------------------------------------------

Let's make ``myconf.py``, enable its execution (``-x`` permission and ``#!``).

There we configure it using nice ``PythonSection`` preset to run our web app.

.. code-block:: python

    #! /usr/bin/env python3
    from uwsgiconf.presets.nice import PythonSection


    PythonSection(
        # Reload uWSGI when this file is updated.
        touch_reload=__file__,

        python_params=dict(
            python_home='/home/idle/venv/',
            search_path='/home/idle/apps/',
        ),

        # Load wsgi.py module from myapp package.
        wsgi_module='myapp.wsgi',

    ).networking.register_socket(
        # Make app available at http://127.0.0.1:8000
        address='127.0.0.1:8000',
        type=PythonSection.networking.socket_types.HTTP,

    ).as_configuration().print_ini()

Now we are ready to use this configuration dynamically (see ``Strategies`` paragraph above).


Configuration with multiple sections
------------------------------------

Let's configure uWSGI to use Emperor Broodlord mode as described here_.

.. _here: http://uwsgi-docs.readthedocs.io/en/latest/Broodlord.html#a-simple-example


.. code-block:: python

    from uwsgiconf import Configuration, Section


    BROODLORD_SOCKET = '/tmp/broodlord.sock'

    # We'll use the same basic params both for Broodlord Emperor and his zergs.
    base_section = (
        Section().
            master_process.set_basic_params(enable=True).
            workers.set_basic_params(count=1).
            python.set_wsgi_params(module='werkzeug.testapp:test_app').
            logging.set_basic_params(no_requests=True))


    # Now we add two sections based on common parameters into our configuration:
    Configuration([

        # This section is for Broodlord Emperor.
        Section.derive_from(base_section).
            networking.register_socket(address=':3031').
            workers.set_zerg_server_params(socket=BROODLORD_SOCKET).
            empire.set_emperor_params(vassals_home='/etc/vassals').
            empire.set_mode_broodlord_params(zerg_count=40, vassal_backlog_items_sos=10),

        # And this one is for zergs.
        Section.derive_from(base_section, name='zerg').
            workers.set_zerg_client_params(server_sockets=BROODLORD_SOCKET).
            master_process.set_idle_params(timeout=30, exit=True)

    ]).print_ini()
