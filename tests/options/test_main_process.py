from uwsgiconf.config import Section


def test_main_process_basics(assert_lines):

    assert_lines([
        'touch-reload = /here/a',
    ], Section().main_process.set_basic_params(touch_reload='/here/a'))

    assert_lines([
        'daemonize = /here/app.log',
    ], Section().main_process.daemonize('/here/app.log'))

    assert_lines([
        'daemonize2 = /here/app.log',
    ], Section().main_process.daemonize('/here/app.log', after_app_loading=True))

    assert_lines([
        'pidfile = /here/file',
    ], Section().main_process.set_pid_file('/here/file'))

    assert_lines([
        'safe-pidfile2 = /here/file',
    ], Section().main_process.set_pid_file(
        '/here/file', before_priv_drop=False, safe=True))

    assert_lines([
        'auto-procname = true',
    ], Section().main_process.set_naming_params(autonaming=True))

    assert_lines([
        'uid = 1001',
    ], Section().main_process.set_owner_params(uid=1001))

    assert_lines([
        'exec-asap = date',
    ], Section().main_process.run_command_on_event('date'))

    assert_lines([
        'touch-exec = myfile.txt date',
    ], Section().main_process.run_command_on_touch('date', 'myfile.txt'))

    assert_lines([
        'skip-atexit = true',
    ], Section().main_process.set_on_exit_params(skip_hooks=True))

    assert_lines([
        'chdir = /here',
    ], Section().main_process.change_dir('/here'))


def test_main_process_advanced(assert_lines):
    assert_lines([
        'ksm = 10',
    ], Section().main_process.set_memory_params(ksm_interval=10))


def test_main_process_hooks(assert_lines):

    section = Section()

    prc = section.main_process
    asap = prc.phases.ASAP

    prc.set_hook(asap, prc.actions.mount('/proc', 'proc', 'none'))
    prc.set_hook(asap, prc.actions.mount('/proc', flags=['rec', 'detach']))
    prc.set_hook(asap, prc.actions.execute('cat /proc/self/mounts'))
    prc.set_hook(asap, prc.actions.call('uwsgi_log application has been loaded'))
    prc.set_hook(asap, prc.actions.call('putenv PATH=bin:$(PATH)', arg_int=True))
    prc.set_hook(asap, prc.actions.call('some', honour_exit_status=True))
    prc.set_hook(asap, prc.actions.dir_change('/here'))
    prc.set_hook(asap, prc.actions.exit())
    prc.set_hook(prc.phases.APP_LOAD_PRE, prc.actions.exit(10))
    prc.set_hook(asap, prc.actions.printout('bingo-bongo'))
    prc.set_hook(asap, prc.actions.file_write('/here/a.txt', 'sometext', append=True, newline=True))
    prc.set_hook(asap, prc.actions.fifo_write('/here/b', '10', wait=True))
    prc.set_hook(asap, prc.actions.unlink('/here/d'))
    prc.set_hook(asap, prc.actions.alarm('myal', 'bang'))
    prc.set_hook(asap, prc.actions.set_host_name('newname'))
    prc.set_hook(asap, prc.actions.file_create('/here/a.txt'))
    prc.set_hook(asap, prc.actions.dir_create('/here/there'))

    assert_lines([
        'hook-asap = mount:proc none /proc',
        'hook-asap = umount:/proc rec,detach',
        'hook-asap = print:bingo-bongo',
        'hook-asap = exec:cat /proc/self/mounts',
        'hook-asap = call:uwsgi_log application has been loaded',
        'hook-asap = callint:putenv PATH=bin:$(PATH)',
        'hook-asap = callret:some',
        'hook-asap = cd:/here',
        'hook-asap = exit:',
        'hook-pre-app = exit:10',
        'hook-asap = appendn:/here/a.txt sometext',
        'hook-asap = spinningfifo:/here/b 10',
        'hook-asap = unlink:/here/d',
        'hook-asap = alarm:myal bang',
        'hook-asap = hostname:newname',
        'hook-asap = create:/here/a.txt',
        'hook-asap = mkdir:/here/there',
    ], section)

    assert_lines([
        'hook-touch = /that do',
    ], Section().main_process.set_hook_touch('/that', 'do'))

    assert_lines([
        'after-request-hook = cfunc',
    ], Section().main_process.set_hook_after_request('cfunc'))
