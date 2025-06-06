"""
JSON logging demo. It shows how to configure uWSGI to format log as JSON.

    Start uWSGI with the following command:

        uwsgiconf run <path-to-this-file>

"""
import logging
from datetime import datetime, timezone
from functools import partial

from uwsgiconf.config import configure_uwsgi
from uwsgiconf.runtime.logging import log_message
from uwsgiconf.runtime.scheduling import register_timer


def encode(data):
    return map(partial(bytes, encoding='utf8'), data)


@register_timer(5)
def log_msg(sig):
    log_message('msg runtime')


def application(env, start_response):

    start_response('200 OK', [('Content-Type','text/html')])

    data = [
        '<h1>uwsgiconf demo: logging JSON</h1>',
        f'<div>updated {datetime.now(tz=timezone.utc)}</div>',
    ]

    logging.warning('msg logging')

    return encode(data)


def configure():
    from pathlib import Path

    from uwsgiconf.presets.nice import PythonSection

    filepath = Path(__file__).absolute()
    port = 8000

    section = PythonSection.bootstrap(
        f'http://127.0.0.1:{port}',
        touch_reload=filepath,
        wsgi_module=filepath,
        workers=1,
    )

    section.configure_logging_json(
        tpl_msg='%(method)>%(status) %(msecs)ms %(vhost)%(uri)',
        tpl_ctx={
            'dt': '__dt_iso__',
            'logger': '__src__',
            'message': '__msg__',
            'ctx': {
                'http_referrer': '%(referer)',
                'http_user_agent': '%(uagent)',
            }
        }
    )

    return section


configure_uwsgi(configure)


if __name__ == '__main__':
    from uwsgiconf.utils import run_uwsgi
    run_uwsgi()
