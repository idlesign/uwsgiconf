import os
from tempfile import NamedTemporaryFile, gettempdir
import pytest

from uwsgiconf.config import Section, Configuration
from uwsgiconf.presets.nice import Section as NiceSection
from uwsgiconf.exceptions import ConfigurationError


def test_section_basics(assert_lines):

    assert_lines('set-placeholder = one=two', Section().set_placeholder('one', 'two'))

    my_section = Section()

    assert_lines('automatically generated', my_section, stamp=True)

    my_section.set_basic_params(strict_config=True)

    assert_lines([
        'uwsgi',
        'strict',
    ], my_section)

    # unset bool
    my_section.set_basic_params(strict_config=False)
    assert_lines([
        'strict',
    ], my_section, assert_in=False)

    # successive unset bool
    my_section.set_basic_params(strict_config=False)

    assert_lines('plugins-list = true', Section().print_plugins())

    # __call__ -> set_basic_params
    assert_lines('workers = 10', Section().workers(count=10))

    # bogus basic params handling. test for no error
    Section(
        params_networking=None,
        params_nonexistent={'a': 'b'},
        dummy_key=1,
    )


def test_bootstrap(assert_lines):

    section = NiceSection.bootstrap('http://1.1.1.1:2222')
    assert_lines('http-socket = 1.1.1.1:2222', section)

    section = NiceSection.bootstrap([
        'http://:80',
        'https://:443?cert=/here/there.crt&key=/that/my.key',
    ])
    assert_lines([
        'shared-socket = :80',
        'shared-socket = :443',
        'http-socket = =0',
        'https-socket = =1,/here/there.crt,/that/my.key',
    ], section)


def test_section_embeddeding_plugins(assert_lines, mock_popen):
    # Embedded plugins handling.
    section = Section(embedded_plugins=Section.embedded_plugins_presets.BASIC)
    assert_lines([
        'plugin = syslog'
    ], section.logging.add_logger(section.logging.loggers.syslog('some')), assert_in=False)

    mock_popen(lambda: (b'plugins ***\nsyslog', b''))

    # Probing.
    section = Section(embedded_plugins=Section.embedded_plugins_presets.PROBE)
    assert_lines([
        'plugin = syslog'
    ], section.logging.add_logger(section.logging.loggers.syslog('some')), assert_in=False)

    section = Section(embedded_plugins=Section.embedded_plugins_presets.PROBE('/venv/bin/uwsgi'))
    assert_lines([
        'plugin = syslog'
    ], section.logging.add_logger(section.logging.loggers.syslog('some')), assert_in=False)


def test_section_print(assert_lines):

    assert_lines('%[[37;49mAAA a%[[0m', Section(style_prints=True).print_out('a', indent='AAA '))
    assert_lines('= >   ===== variables', Section().print_variables())


def test_section_fallback(assert_lines):

    assert_lines('fallback-config = a/b.ini', Section().set_fallback('a/b.ini'))
    assert_lines('fallback-config = :here', Section().set_fallback(Section(name='here')))


def test_section_env(assert_lines):
    os.environ['Q'] = 'qq'

    assert_lines([
        'env = A=aa',
        'unenv = B',
        'env = Q=qq',
    ], Section().env('A', 'aa').env('Q').env('B', unset=True))


def test_section_include(assert_lines):

    assert_lines('ini = a/b.ini', Section().include('a/b.ini'))
    assert_lines('ini = :here', Section().include(Section(name='here')))


def test_section_derive_from(assert_lines):
    sec_base = Section(name='mine').workers.set_basic_params(count=3)

    assert_lines([
        '[mine]',
        'workers = 3',
    ], sec_base)

    sec1 = (
        Section.derive_from(sec_base).
            workers.set_basic_params(count=4).master_process.set_basic_params(enable=True))

    sec2 = (
        Section.derive_from(sec_base, name='other').
            workers.set_thread_params(enable=True))

    assert_lines([
        '[mine]',
        'workers = 4',
    ], sec1)

    assert_lines([
        '[other]',
        'workers = 3',
        'enable-threads = true',
    ], sec2)


def test_section_plugins(assert_lines):

    assert_lines([
        'plugins-dir = /here\nplugins-dir = /there\nplugin = plug',
    ], Section().set_plugins_params(
        plugins='plug', search_dirs=['/here', '/there'], autoload=True
    ))

    section = Section()
    assert hash(section.python) == hash(section.python.name)


def test_plugin_init(assert_lines):
    assert_lines([
        'plugin = python34',

    ], Section(params_python={'version': 34, 'python_home': '/here'}))


def test_configuration(capsys, assert_lines):

    # basic params init
    assert_lines([
        'workers = 33',

    ], Section(params_workers=dict(count=33)))

    assert 'testit' in Section().as_configuration(alias='testit').tofile()

    fpath = NamedTemporaryFile(delete=False).name

    assert fpath == Section().as_configuration().tofile(fpath)

    assert Section().as_configuration(alias='uwsgitest').tofile(gettempdir()).endswith('uwsgitest.ini')

    s1 = Section()
    s2 = 'some'

    with pytest.raises(ConfigurationError) as einfo:
        Configuration([s1, s2]).format()
    assert 'Section' in str(einfo.value)  # is a section

    s2 = Section()

    with pytest.raises(ConfigurationError) as einfo:
        Configuration([s1, s2]).format()
    assert 'unique' in str(einfo.value)  # has unique name

    s2.name = 'another'

    assert 'ini = :another' in Configuration([s1, s2], autoinclude_sections=True).format()

    assert Configuration([s1, s2]).print_ini()


def test_args_formatter(capsys, assert_lines):

    formatted = NiceSection.bootstrap(
        'http://localhost:8000'
    ).logging.set_basic_params(template='%(pid)').as_configuration().format(formatter='args')

    assert '>   This configuration was automatically generated using' in formatted
    assert '--master' in formatted
    assert 'true' not in formatted  # no values for bools
    assert '%k' not in formatted  # no config vars support for CLI
    assert '%(pid)' in formatted
