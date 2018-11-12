Contrib
=======

Additional integrations with third parties.


Django uwsigify
---------------

``uwsgify`` adds integration with Django Framework.

First add ``uwsgify`` into ``INSTALLED_APPS``.

.. code-block:: python

    INSTALLED_APPS = [
        ...
        'uwsgiconf.contrib.django.uwsgify',
        ...
    ]



uwsgi_run
~~~~~~~~~

``uwsgi_run`` management command runs uWSGI to serve your Django-based project.

.. code-block:: bash

    $ ./manage.py uwsgi_run

    ; Options are available, use --help switch to get help.
    $ ./manage.py uwsgi_run --help


Now your project is up and running on ``http://127.0.0.1:8000``.

By default the command runs your project using some defaults, but you can configure it to your needs
with the help of ``uwsgicfg.py`` (constructed in a usual for **uwsgiconf** manner) placed near your ``manage.py``.


.. code-block:: python

    from uwsgiconf.config import configure_uwsgi


    def get_configurations():

        from os.path import dirname, abspath, join
        from uwsgiconf.presets.nice import PythonSection

        section = PythonSection(
            wsgi_module=join(dirname(abspath(__file__)), 'wsgi.py')

        ).networking.register_socket(
            PythonSection.networking.sockets.http('127.0.0.1:8000')
        )

        ...

        return section


    configure_uwsgi(get_configurations)


uwsgi_reload
~~~~~~~~~~~~

``uwsgi_reload`` management command reloads uWSGI master process, workers.

.. code-block:: bash

    $ ./manage.py uwsgi_reload

    ; Options are available, use --help switch to get help.
    $ ./manage.py uwsgi_reload --help
