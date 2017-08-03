Tips and hints
==============


How to get through
------------------

*There are some many options, how to start?*

Start with a preset configuration. For example, if you have a Python web-app try out ``uwsgiconf.presets.nice.PythonSection``.
Basic things to do are: define ``wsgi_module`` and do ``.networking.register_socket``.

This should already give a more or less decent decent configuration. 

After that you can skim through option groups (such as ``.networking``, ``.main_process``, ``.workers`` etc.) 
and deep into uWSGI abilities.


Use from virtualenv
-------------------

*I have a virtualenv in venv/ directory (where I have uWSGI and uwsgiconf) and 
configuration module outside of it, how do I run it?*

You can try the following trick (from directory containing ``venv/`` and ``uwsgicfg.py``):

.. code-block:: bash

    $ venv/bin/uwsgi --ini "exec://venv/bin/python uwsgicfg.py"


Install with CLI
----------------
*I'm unable to run CLI because of a strange error, what should I do?*

**uwsgiconf** expects ``click`` package available for CLI but won't install this dependency by default.

Use the following command to install **uwsgiconf** with ``click``:

.. code-block:: bash

    $ pip install uwsgiconf[cli]

