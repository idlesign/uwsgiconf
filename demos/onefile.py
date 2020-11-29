"""
Trick demo. It shows how to use one file both for uWSGI configuration and application definition.

    Start uWSGI with the following command:

        uwsgiconf run <path-to-this-file>

"""
from functools import partial

from uwsgiconf.config import configure_uwsgi


def encode(data):
    return map(partial(bytes, encoding='utf8'), data)


def app_1(env, start_response):
    """This is simple WSGI application that will be served by uWSGI."""

    from uwsgiconf.runtime.platform import uwsgi

    start_response('200 OK', [('Content-Type','text/html')])

    data = [
        '<h1>uwsgiconf demo: one file</h1>',

        f'<div>uWSGI version: {uwsgi.get_version()}</div>',
        f'<div>uWSGI request ID: {uwsgi.request.id}</div>',
    ]

    return encode(data)


def app_2(env, start_response):
    """This is another simple WSGI application that will be served by uWSGI."""

    import random

    start_response('200 OK', [('Content-Type','text/html')])

    data = [
        '<h1>uwsgiconf demo: one file second app</h1>',

        f'<div>Some random number for you: {random.randint(1, 99999)}</div>',
    ]

    return encode(data)


def configure():
    """Configure uWSGI.

    This returns several configuration objects, which will be used
    to spawn several uWSGI processes.

    Applications are on 127.0.0.1 on ports starting from 8000.

    """
    from pathlib import Path
    from uwsgiconf.presets.nice import PythonSection

    filepath = Path(__file__).absolute()
    port = 8000

    configurations = []

    for idx in range(2):

        alias = f'app_{idx + 1}'

        section = PythonSection.bootstrap(

            f'http://127.0.0.1:{port}',

            # Automatically reload uWSGI if this file is changed.
            touch_reload=filepath,

            # To differentiate easily.
            process_prefix=alias,

            # Serve WSGI application (see above) from this very file.
            wsgi_module=filepath,

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
