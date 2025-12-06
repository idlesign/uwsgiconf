from uwsgiconf.config import configure_uwsgi
from uwsgiconf.options.workers import MuleFarm


def get_configurations():
    from uwsgiconf.presets.nice import PythonSection
    section = PythonSection(name='testdummy')
    section.caching.add_cache("mycache", max_items=10)
    section.workers.set_mules_params(
        farms=[
            MuleFarm(name='farm1', mule_numbers=3),
        ]
    )
    return section


configure_uwsgi(get_configurations)
