from uwsgiconf.config import configure_uwsgi


def get_configurations():
    from uwsgiconf.presets.nice import PythonSection
    section = PythonSection(name='testdummy')
    section.caching.add_cache("mycache", max_items=10)
    return section


configure_uwsgi(get_configurations)
