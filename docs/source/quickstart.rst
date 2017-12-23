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

Let's make ``uwsgicfg.py``. There we configure uWSGI using nice ``PythonSection`` preset to run our web app.

.. code-block:: python

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
                # Let's add something into Python path.
                search_path='/opt/apps_shared/',
            ),

            wsgi_module=my_app_dir + 'wsgi.py',

            # We'll redirect logs into a file.
            log_into=my_app_dir + 'app.log',

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

Let's configure uWSGI to use Emperor Broodlord mode as described here_ using ``Broodlord`` preset.

.. _here: http://uwsgi-docs.readthedocs.io/en/latest/Broodlord.html#a-simple-example


.. code-block:: python

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
