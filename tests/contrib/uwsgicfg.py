from uwsgiconf.config import configure_uwsgi


def get_configurations():
    from uwsgiconf.presets.nice import PythonSection
    section = PythonSection(name='testdummy')
    return section


configure_uwsgi(get_configurations)
