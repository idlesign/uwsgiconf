import pytest

from uwsgiconf.config import Section
from uwsgiconf.exceptions import ConfigurationError


def test_plugin_python_basics(assert_lines):

    def get_plugin_group():
        section = Section()
        return section.python

    assert_lines([
        'enable-threads = true',
    ], get_plugin_group().set_basic_params(enable_threads=True))

    assert_lines([
        'pyargv = a b',
    ], get_plugin_group().set_app_args('a', 'b'))

    assert_lines([
        'wsgi = myapp.py',
    ], get_plugin_group().set_wsgi_params(module='myapp.py'))

    assert_lines([
        'wsgi-file = some/file.py',
    ], get_plugin_group().set_wsgi_params(module='some/file.py'))

    assert_lines([
        'eval = print("!")',
    ], get_plugin_group().eval_wsgi_entrypoint(code='print("!")'))

    assert_lines([
        'py-auto-reload = 10',
    ], get_plugin_group().set_autoreload_params(scan_interval=10))

    assert_lines([
        'post-pymodule-alias = ali=here/file.py',
    ], get_plugin_group().register_module_alias('ali', 'here/file.py', after_init=True))

    assert_lines([
        'post-pymodule-alias = ali=here/file.py',
    ], get_plugin_group().register_module_alias('ali', 'here/file.py', after_init=True))

    with pytest.raises(ConfigurationError) as einfo:
        assert_lines('', get_plugin_group().import_module('some.module', shared=True, into_spooler=True))
    assert 'set both' in str(einfo.value)

    assert_lines([
        'python-import = some/module.py',
    ], get_plugin_group().import_module('some/module.py'))

    assert_lines([
        'shared-python-import = some/sharemodule.py',
    ], get_plugin_group().import_module('some/sharemodule.py', shared=True))

    assert_lines([
        'spooler-python-import = some/forspooler.py',
    ], get_plugin_group().import_module('some/forspooler.py', into_spooler=True))

    assert_lines([
        'pyrun = runit.py',
    ], get_plugin_group().run_module('runit.py'))
