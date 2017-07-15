Quickstart
==========

Strategies
----------

Two main strategies to use **uwsgiconf**:

1. **Static:** create configuration .py and compile in on demand into classic uWSGI .ini.
2. **Dynamic:** create configuration .py, make it executable and give it directly to uWSGI

  .. code-block:: bash

    uwsgi --ini 'exec://path/to/myconf.py'


Using preset to run Python web application
------------------------------------------

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
        address='127.0.0.1:8000'

    ).as_configuration().print_ini()

Now we are ready to use this configuration dynamically (see ``Strategies`` paragraph above).
