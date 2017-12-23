from uwsgiconf.config import Section
from uwsgiconf.presets.empire import Broodlord


def test_broodlord(assert_lines):

    emperor, zerg = Broodlord(

        zerg_socket='/tmp/broodlord.sock',
        zerg_count=40,
        zerg_die_on_idle=30,
        vassals_home='/etc/vassals',
        vassal_queue_items_sos=10,

        section_emperor=(Section().
            master_process(enable=True).
            workers(count=1).
            logging(no_requests=True).
            python.set_wsgi_params(module='werkzeug.testapp:test_app')
        )

    ).configure()

    emperor.networking.register_socket(Section.networking.sockets.default(':3031'))

    assert_lines([
        'master = true',
        'workers = 1',
        'disable-logging = true',
        'wsgi = werkzeug.testapp:test_app',
        'zerg-server = /tmp/broodlord.sock',
        'emperor = /etc/vassals',
        'emperor-broodlord = 40',
        'vassal-sos-backlog = 10',
        'socket = :3031',
    ], emperor)

    assert_lines([
        'master = true',
        'workers = 1',
        'disable-logging = true',
        'wsgi = werkzeug.testapp:test_app',
        'idle = 30',
        'die-on-idle = true',
    ], zerg)
