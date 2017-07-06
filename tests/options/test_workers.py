from uwsgiconf import Section


def test_workers_basics(assert_lines):

    assert_lines([
        'workers = 3',
    ], Section().grp_workers.set_basic_params(count=3))

    assert_lines([
        'threads = 2',
    ], Section().grp_workers.set_thread_params(per_worker=2))

    assert_lines([
        'min-worker-lifetime = 10',
    ], Section().grp_workers.set_reload_params(min_lifetime=10))

    assert_lines([
        'reload-on-exception = true',
    ], Section().grp_workers.set_reload_on_exception_params(do_reload=True))

    assert_lines([
        'harakiri = 20',
    ], Section().grp_workers.set_harakiri_params(timeout=20))

    assert_lines([
        'worker-exec = date',
    ], Section().grp_workers.run_command_as_worker('date'))


def test_mules(assert_lines):

    assert_lines([
        'mule-harakiri = 3',
    ], Section().grp_workers.set_mules_params(harakiri_timeout=3))

    section = Section()

    assert_lines([
        'farm = first:1,2',
        'farm = second:3,4,5',
        'mules = 5',

    ], section.grp_workers.set_mules_params(farms=[
        section.grp_workers.cls_mule_farm('first', 2),
        section.grp_workers.cls_mule_farm('second', 3),
    ]))

    assert_lines([
        'mule = mule1.py',
        'mule = mule2.py',

    ], Section().grp_workers.set_mules_params(mules=[
        'mule1.py',
        'mule2.py',
    ]))


