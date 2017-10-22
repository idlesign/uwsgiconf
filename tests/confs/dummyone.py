from uwsgiconf.config import Section, configure_uwsgi


uwsgi_configuration = configure_uwsgi(lambda: Section())
