Quickstart
==========


Install
-------

You can get and install **uwsgiconf** from PyPI using ``pip``:

.. code-block:: bash

    $ pip install uwsgiconf


CLI
~~~

**uwsgiconf** expects ``click`` package available for CLI but won't install this dependency by default.

Use the following command to install **uwsgiconf** with ``click``:

.. code-block:: bash

    $ pip install uwsgiconf[cli]


Using a preset to run Python web application
--------------------------------------------

Let's make ``uwsgicfg.py``. There we configure it using nice ``PythonSection`` preset to run our web app.

.. code-block:: python

    from uwsgiconf.config import configure_uwsgi
    from uwsgiconf.presets.nice import PythonSection


    def get_configurations():
        """This should return one or more Section or Configuration objects.
        In such a way you can configure more than one uWSGI instance in the same place.

        """
        section = PythonSection(
            # Reload uWSGI when this file is updated.
            touch_reload=__file__,

            params_python=dict(
                # Let's add something into Python path.
                search_path='/home/idle/apps/',
            ),

            wsgi_module='/home/idle/myapp/wsgi.py',

            # If your uWSGI has no basic plugins embedded
            # (i.e. not from PyPI) you can give uwsgiconf a hint:
            # embedded_plugins=False,

        ).networking.register_socket(
            # Make app available at http://127.0.0.1:8000
            PythonSection.networking.sockets.http('127.0.0.1:8000'))

        return section


    # Almost done. One more thing:
    configure_uwsgi(get_configurations)


Now we are ready to use this configuration:

.. code-block:: bash

    $ uwsgiconf compile > myconf.ini
    $ uwsgi myconf.ini

    ; or instead just
    $ uwsgiconf run


Configuration with multiple sections
------------------------------------

Let's configure uWSGI to use Emperor Broodlord mode as described here_.

.. _here: http://uwsgi-docs.readthedocs.io/en/latest/Broodlord.html#a-simple-example


.. code-block:: python

    from uwsgiconf.config import Configuration, Section


    BROODLORD_SOCKET = '/tmp/broodlord.sock'

    # We'll use the same basic params both for Broodlord Emperor and his zergs.
    base_section = (
        Section().
            master_process.set_basic_params(enable=True).
            workers.set_basic_params(count=1).
            logging.set_basic_params(no_requests=True).
            python.set_wsgi_params(module='werkzeug.testapp:test_app'))
            
    # NOTE. There is a shortcut for ``set_basic_params`` methods:
    # Instead of `master_process.set_basic_params(enable=True)`
    # you can say plain `master_process(enable=True)`, yet
    # in than case you won't get any arg hints from you IDE.

    # Now we add two sections based on common parameters into our configuration:
    configuration = Configuration([

        # This section is for Broodlord Emperor.
        Section.derive_from(base_section).
            networking.register_socket(Section.networking.sockets.default(':3031')).
            workers.set_zerg_server_params(socket=BROODLORD_SOCKET).
            empire.set_emperor_params(vassals_home='/etc/vassals').
            empire.set_mode_broodlord_params(zerg_count=40, vassal_backlog_items_sos=10),

        # And this one is for zergs.
        Section.derive_from(base_section, name='zerg').
            workers.set_zerg_client_params(server_sockets=BROODLORD_SOCKET).
            master_process.set_idle_params(timeout=30, exit=True)

    ])
