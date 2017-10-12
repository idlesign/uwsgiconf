FAQ
===


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

    $ venv/bin/uwsgiconf run


Unknown config directive
------------------------

*I use* ``PythonSection`` *for configuration and get* **[strict-mode] unknown config directive: wsgi-file** *on start. What's that?*

**uwsgiconf** enables configuration options check (aka ``strict-mode``) by default.

If uWSGI plugin which provides some options is not available, you'll get the message. That's because ``PythonSection``
by default won't instruct uWSGI to load Python plugin (since if you get uWSGI from PyPI you already have
Python and a bunch of other plugins embedded, so there's no need to load them).

If you get that message most probably uWSGI is provided by your OS distribution (e.g. on Debian you'll need to install
plugin packages separately from uWSGI itself).

In that case you can try to set ``embedded_plugins=False`` for ``PythonSection`` (see Quickstart example).

Another option is to quickly fire up ``uWSGI`` to check what plugins are embedded (the same can be achieved with
``$ uwsgiconf probe_plugins`` command).

**uwsgiconf** can also do it for you automatically on configuration stage:

.. code-block:: python

    Section(embedded_plugins=Section.embedded_plugins_presets.PROBE)

Using the above, ``embedded_plugins`` will be inhabited by plugins actually available in uWSGI.
