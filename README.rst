uwsgiconf
=========
https://github.com/idlesign/uwsgiconf

|release| |stats|  |lic| |ci| |coverage| |health|

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

.. |health| image:: https://landscape.io/github/idlesign/uwsgiconf/master/landscape.svg?style=flat
    :target: https://landscape.io/github/idlesign/uwsgiconf/master


Description
-----------

*Configure uWSGI from your Python code*

If you think you known uWSGI you're probably wrong. It is always more than you think it is.
There are so many subsystems and options_ it is difficult to even try to wrap your mind around.

.. _options: http://uwsgi-docs.readthedocs.io/en/latest/Options.html

**uwsgiconf** allowing to define uWSGI configurations in Python tries to improve things the following ways:

* It structures options for various subsystems using classes and methods;
* It uses docstrings and sane naming to facilitate navigation;
* It ships some useful presets to reduce boilerplate code;

*Consider using IDE with autocompletion and docstings support to be more productive with uwsgiconf.*

By that time you already know that **uwsgiconf** is just another configuration method. Why_?

.. _Why: http://uwsgi-docs.readthedocs.io/en/latest/FAQ.html#why-do-you-support-multiple-methods-of-configuration


Strategies
----------

Two main strategies to use **uwsgiconf**:

1. **Static.** Create configuration .py and compile in into classic uWSGI .ini.
2. **Dynamic.** Create configuration .py, make it executable and give it directly to uWSGI

  .. code-block:: bash

    uwsgi --ini 'exec://path/to/myconf.py'


Documentation
-------------

http://uwsgiconf.readthedocs.org/


