# -*- encoding: utf-8 -*-
"""
Trick demo. It shows how to use one file both for uWSGI configuration and application definition.

    Start uWSGI with the following command:

        uwsgiconf run <path-to-this-file>

"""
from functools import partial

from uwsgiconf.config import configure_uwsgi
from uwsgiconf.utils import PY3


def encode(data):
    return map(partial(bytes, encoding='utf8'), data) if PY3 else data


def app_1(env, start_response):
    """This is simple WSGI application that will be served by uWSGI."""

    from uwsgiconf.runtime.environ import uwsgi_env

    start_response('200 OK', [('Content-Type','text/html')])

    data = [
        '<h1>uwsgiconf demo: one file</h1>',

        '<div>uWSGI version: %s</div>' % uwsgi_env.get_version(),
        '<div>uWSGI request ID: %s</div>' % uwsgi_env.request.id,
    ]

    return encode(data)


def app_2(env, start_response):
    """This is another simple WSGI application that will be served by uWSGI."""

    import random

    start_response('200 OK', [('Content-Type','text/html')])

    data = [
        '<h1>uwsgiconf demo: one file second app</h1>',

        '<div>Some random number for you: %s</div>' % random.randint(1, 99999),
    ]

    return encode(data)


def configure():
    """Configure uWSGI.

    This returns several configuration objects, which will be used
    to spawn several uWSGI processes.

    Applications are on 127.0.0.1 on ports starting from 8000.

    """
    import os
    from uwsgiconf.presets.nice import PythonSection

    FILE = os.path.abspath(__file__)
    port = 8000

    configurations = []

    for idx in range(2):

        alias = 'app_%s' % (idx + 1)

        section = PythonSection.bootstrap(

            'http://127.0.0.1:%s' % port,

            # Automatically reload uWSGI if this file is changed.
            touch_reload=FILE,

            # To differentiate easily.
            process_prefix=alias,

            # Serve WSGI application (see above) from this very file.
            wsgi_module=FILE,

            # Custom WSGI callable for second app.
            wsgi_callable=alias,

            # One is just enough, no use in worker on every core
            # for this demo.
            workers=1,

        )

        port += 1

        configurations.append(
            # We give alias for configuration to prevent clashes.
            section.as_configuration(alias=alias))

    return configurations


configure_uwsgi(configure)
