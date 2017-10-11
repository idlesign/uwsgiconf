# -*- encoding: utf-8 -*-
"""
Trick demo. It shows how to use one file both for uWSGI configuration and application definition.

    Start uWSGI with the following command:

        uwsgiconf run <path-to-this-file>

* Python 3 is expected.

"""


def application(env, start_response):
    """This is simple WSGI application that will be served by uWSGI."""

    from functools import partial
    import random
    from uwsgiconf.runtime.environ import uwsgi_env

    start_response('200 OK', [('Content-Type','text/html')])

    data = [
        '<h1>uwsgiconf demo: one file</h1>',

        '<div>Some random number for you: %s</div>' % random.randint(1, 99999),

        '<div>uWSGI version: %s</div>' % uwsgi_env.get_version(),
        '<div>uWSGI request ID: %s</div>' % uwsgi_env.request.id,
    ]

    return map(partial(bytes, encoding='utf8'), data)


def configure():
    """Configure uWSGI."""
    import os
    from uwsgiconf.presets.nice import PythonSection

    FILE = os.path.abspath(__file__)

    section = PythonSection(
        # Automatically reload uWSGI if this file is changed.
        touch_reload=FILE,

        # Serve WSGI application (see above) from this very file.
        wsgi_module=FILE,

        # One is just enough, no use in worker on every core
        # for this demo.
        workers=1

    ).networking.register_socket(
        PythonSection.networking.sockets.http('127.0.0.1:8000'),

    )

    return section


configuration = configure()
