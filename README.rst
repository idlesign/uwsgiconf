uwsgiconf
=========
https://github.com/idlesign/uwsgiconf

|release| |stats|  |lic| |ci| |coverage|

.. |release| image:: https://img.shields.io/pypi/v/uwsgiconf.svg
    :target: https://pypi.python.org/pypi/uwsgiconf

.. |stats| image:: https://img.shields.io/pypi/dm/uwsgiconf.svg
    :target: https://pypi.python.org/pypi/uwsgiconf

.. |lic| image:: https://img.shields.io/pypi/l/uwsgiconf.svg
    :target: https://pypi.python.org/pypi/uwsgiconf

.. |ci| image:: https://img.shields.io/travis/idlesign/uwsgiconf/master.svg
    :target: https://travis-ci.org/idlesign/uwsgiconf

.. |coverage| image:: https://img.shields.io/coveralls/idlesign/uwsgiconf/master.svg
    :target: https://coveralls.io/r/idlesign/uwsgiconf


**Work in progress. Stay tuned.**


Description
-----------

*Configure uWSGI from your Python code*

If you think you know uWSGI you're probably wrong. It is always more than you think it is.
There are so many subsystems and options_ (800+) it is difficult to even try to wrap your mind around.

.. _options: http://uwsgi-docs.readthedocs.io/en/latest/Options.html

**uwsgiconf** allowing to define uWSGI configurations in Python tries to improve things the following ways:

* It structures options for various subsystems using classes and methods;
* It uses docstrings and sane naming to facilitate navigation;
* It ships some useful presets to reduce boilerplate code;

*Consider using IDE with autocompletion and docstings support to be more productive with uwsgiconf.*

By that time you already know that **uwsgiconf** is just another configuration method. Why_?

.. _Why: http://uwsgi-docs.readthedocs.io/en/latest/FAQ.html#why-do-you-support-multiple-methods-of-configuration

Moreover **uwsgiconf** comes with CLI to facilitate configuration.


Usage Strategies
----------------

Two main strategies to use **uwsgiconf**:

1. **Static:** create configuration ``.py`` and compile it on demand into classic uWSGI ``.ini`` using provided methods.
2. **Dynamic:** create configuration .py, and give it directly to uWSGI with ``exec`` directive.


A taste of it
-------------

Let's make ``uwsgicfg.py``. There we configure it using nice ``PythonSection`` preset to run our web app.

.. code-block:: python

    from uwsgiconf.presets.nice import PythonSection


    configuration = PythonSection(
        # Load wsgi.py module containing WSGI application.
        wsgi_module='/home/idle/myapp/wsgi.py',

    ).networking.register_socket(
        # Make app available at http://127.0.0.1:8000
        address='127.0.0.1:8000',
        type=PythonSection.networking.socket_types.HTTP,

    ).as_configuration()

    configuration.print_ini()

1. Now if you want to generate ``myconf.ini`` file and use it for uWSGI you can do it with:

    .. code-block:: bash

        $ python uwsgicfg.py > myconf.ini
        ; or just
        $ uwsgiconf compile > myconf.ini

        $ uwsgi myconf.ini

2. Or for dynamic usage of .py:

    .. code-block:: bash

        $ uwsgi --ini "exec://python uwsgicfg.py"
        ; or just
        $ uwsgiconf run


Documentation
-------------

http://uwsgiconf.readthedocs.org/
