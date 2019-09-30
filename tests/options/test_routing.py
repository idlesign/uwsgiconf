import pytest

from uwsgiconf.config import Section
from uwsgiconf.exceptions import ConfigurationError


def test_routing_basics(assert_lines):

    assert_lines([
        'routers-list = true',
    ], Section().routing.print_routing_rules())

    assert_lines([
        'error-page-500 = /here/500.html',
    ], Section().routing.set_error_page(500, '/here/500.html'))

    assert_lines([
        'error-page-403 = /there/403.html',
        'error-page-404 = /there/404.html',
        'error-page-500 = /there/500.html',
    ], Section().routing.set_error_pages(common_prefix='/there/'))

    assert_lines([
        'error-page-404 = /opt/missing.html',

    ], Section().routing.set_error_pages(
        {404: 'missing.html'},
        common_prefix='/opt/'))

    assert_lines([
        'error-page-404 = /a/missing.html',
        'error-page-500 = /b/error.html',

    ], Section().routing.set_error_pages(
        {404: '/a/missing.html', 500: '/b/error.html'}))

    with pytest.raises(ConfigurationError):  # unsupported code
        assert_lines('', Section().routing.set_error_page(800, '/here/800.html'))

    assert_lines([
        'plugin = geoip\ngeoip-city = GeoLiteCity.dat',
    ], Section().routing.set_geoip_params(db_city='GeoLiteCity.dat'))

    assert_lines([
        'del-header = Connection',
    ], Section().routing.header_remove('Connection'))

    assert_lines([
        'add-header = Connection: Keep-Alive',
    ], Section().routing.header_add('Connection', 'Keep-Alive'))

    assert_lines([
        'pull-header = X-Offload-to-SSE X_OFFLOAD',
    ], Section().routing.header_collect('X-Offload-to-SSE', 'X_OFFLOAD', pull=True))

    assert_lines([
        'collect-header = Content-Type CONTENT_TYPE',
    ], Section().routing.header_collect('Content-Type', 'CONTENT_TYPE'))


def test_routing_rules(assert_lines):
    rule = Section.routing.route_rule

    assert_lines([
        'response-route-run = continue:',

    ], Section().routing.register_route(
        rule(
            rule.actions.do_continue(),
            subject=None,
            stage=rule.stages.RESPONSE)
    ))

    assert_lines([
        'route-if-not = eq:${PATH_INFO};/bad chdir:/here',

    ], Section().routing.register_route(
        rule(
            rule.actions.dir_change('/here'),
            ~rule.subjects.custom(rule.vars.request('PATH_INFO')).eq('/bad'))
    ))

    assert_lines([
        'route = ^/redir redirect-302:http://here',

    ], Section().routing.register_route(
        rule(
            rule.actions.redirect('http://here'),
            subject='^/redir',
        )
    ))


def test_routing_subject_custom():

    subj = Section.routing.route_rule.subjects.custom('mysubj')

    assert str(subj.exists()) == 'exists:mysubj'
    assert str(subj.isfile()) == 'isfile:mysubj'
    assert str(subj.isdir()) == 'isdir:mysubj'
    assert str(subj.islink()) == 'islink:mysubj'
    assert str(subj.isexec()) == 'isexec:mysubj'

    assert str(subj.eq(33)) == 'eq:mysubj;33'
    assert str(subj.ge(33)) == 'ishigherequal:mysubj;33'
    assert str(subj.le(33)) == 'islowerequal:mysubj;33'
    assert str(subj.gt(33)) == 'ishigher:mysubj;33'
    assert str(subj.lt(33)) == 'islower:mysubj;33'

    assert str(subj.isempty()) == 'empty:mysubj'
    assert str(subj.startswith('my')) == 'startswith:mysubj;my'
    assert str(subj.endswith('bj')) == 'endswith:mysubj;bj'
    assert str(subj.matches('mys')) == 'regexp:mysubj;mys'
    assert str(subj.contains('sub')) == 'contains:mysubj;sub'
    assert str(subj.contains_ipv4()) == 'ipv4in:mysubj'
    assert str(subj.contains_ipv6()) == 'ipv6in:mysubj'

    assert str(subj.islord()) == 'lord:mysubj'


def test_routing_transformations(assert_lines):

    rule = Section.routing.route_rule

    assert_lines(
        'route-run = forcexcl:',
        Section().routing.register_route(rule(
            rule.transforms.fix_content_len(add_header=True), subject=None))
    )

    assert_lines(
        'route-run = flush:',
        Section().routing.register_route(rule(rule.transforms.flush(), subject=None))
    )

    assert_lines(
        'route-run = gzip:',
        Section().routing.register_route(rule(rule.transforms.gzip(), subject=None))
    )

    assert_lines(
        'route-run = toupper:',
        Section().routing.register_route(rule(rule.transforms.upper(), subject=None))
    )

    assert_lines(
        'route-run = tofile:filename=/tmp/mycache',
        Section().routing.register_route(rule(rule.transforms.to_file('/tmp/mycache'), subject=None))
    )

    assert_lines(
        'route-run = chunked:',
        Section().routing.register_route(rule(rule.transforms.chunked(), subject=None))
    )

    assert_lines(
        'route-run = template:',
        Section().routing.register_route(rule(rule.transforms.template(), subject=None))
    )


def test_routing_actions(assert_lines):

    rule = Section.routing.route_rule

    assert_lines([
        'route-run = continue:',

    ], Section().routing.register_route(
        rule(rule.actions.do_continue(), subject=None)
    ))

    assert_lines([
        'route-run = send-crnl:HTTP/1.0 100 Continue',

    ], Section().routing.register_route(
        rule(rule.actions.send('HTTP/1.0 100 Continue', crnl=True), subject=None)
    ))

    assert_lines([
        'plugin = router_uwsgi',
        'route-run = uwsgi:127.0.0.1:3031,5,,fooapp',

    ], Section().routing.register_route(
        rule(rule.actions.route_uwsgi(
            '127.0.0.1:3031', modifier=Section.routing.modifiers.psgi(), app='fooapp'), subject=None)
    ))

    assert_lines([
        'plugin = router_rewrite',
        'route-uri = /some rewrite-last:/index.php?page=$1.php',

    ], Section().routing.register_route(
        rule(
            rule.actions.rewrite('/index.php?page=$1.php', do_continue=True),
            subject=rule.subjects.request_uri('/some'))
    ))

    assert_lines([
        'plugin = router_redirect',
        'route-run = redirect-301:http://here',

    ], Section().routing.register_route(
        rule(rule.actions.redirect('http://here', permanent=True), subject=None)
    ))

    assert_lines([
        'route-run = return:500',

    ], Section().routing.register_route(
        rule(rule.actions.do_break(500, return_body=True), subject=None)
    ))

    assert_lines([
        'route-run = donotlog:',

    ], Section().routing.register_route(
        rule(rule.actions.log(None), subject=None)
    ))

    assert_lines([
        'route-run = donotoffload:',

    ], Section().routing.register_route(
        rule(rule.actions.offload_off(), subject=None)
    ))

    assert_lines([
        'route-run = logvar:myvar $1',

    ], Section().routing.register_route(
        rule(rule.actions.add_var_log('myvar', '$1'), subject=None)
    ))

    assert_lines([
        'route-run = goto:here',

    ], Section().routing.register_route(
        rule(rule.actions.do_goto('here'), subject=None)
    ))

    assert_lines([
        'route-run = addvar:MY_CGI myval',

    ], Section().routing.register_route(
        rule(rule.actions.add_var_cgi('MY_CGI', 'myval'), subject=None)
    ))

    assert_lines([
        'route-run = addheader:Content-Type: text/html',

    ], Section().routing.register_route(
        rule(rule.actions.header_add('Content-Type', 'text/html'), subject=None)
    ))

    assert_lines([
        'route-run = delheader:Content-Type',

    ], Section().routing.register_route(
        rule(rule.actions.header_remove('Content-Type'), subject=None)
    ))

    assert_lines([
        'route-run = disableheaders:',

    ], Section().routing.register_route(
        rule(rule.actions.headers_off(), subject=None)
    ))

    assert_lines([
        'route-run = clearheaders:200',

    ], Section().routing.register_route(
        rule(rule.actions.headers_reset(200), subject=None)
    ))

    assert_lines([
        'route-run = clearheaders:200',

    ], Section().routing.register_route(
        rule(rule.actions.headers_reset(200), subject=None)
    ))

    assert_lines([
        'route-run = signal:33',

    ], Section().routing.register_route(
        rule(rule.actions.signal(33), subject=None)
    ))

    assert_lines([
        'plugin = router_http',
        'route-run = http:127.0.0.1:8181,my.domain.ru',

    ], Section().routing.register_route(
        rule(rule.actions.route_external('127.0.0.1:8181', 'my.domain.ru'), subject=None)
    ))


    assert_lines([
        'plugin = router_static',
        'route-run = static:/here/a.jpg',

    ], Section().routing.register_route(
        rule(rule.actions.serve_static('/here/a.jpg'), subject=None)
    ))

    assert_lines([
        'plugin = router_basicauth',
        'route-run = basicauth-next:my realm,usr:pwd',
        'route-run = basicauth:my realm,htpwd',
        'route-run = basicauth:my realm,ussr:',

    ], Section().routing.register_route([
        rule(rule.actions.auth_basic('my realm', 'usr', 'pwd', do_next=True), subject=None),
        rule(rule.actions.auth_basic('my realm', password='htpwd'), subject=None),
        rule(rule.actions.auth_basic('my realm', 'ussr'), subject=None),
    ]))

    assert_lines([
        'plugin = ldap',
        'route-run = ldapauth-next:my realm,url=ldap://ldap.domain.com;basedn=ou=users,dc=domain;loglevel=1',

    ], Section().routing.register_route([
        rule(rule.actions.auth_ldap(
            'my realm', 'ldap://ldap.domain.com', base_dn='ou=users,dc=domain', log_level=1,
            do_next=True), subject=None),
    ]))

    assert_lines([
        'route-run = chdir:/here',

    ], Section().routing.register_route([
        rule(rule.actions.dir_change('/here'), subject=None),
    ]))

    assert_lines([
        'route-run = setapp:myapp',

    ], Section().routing.register_route([
        rule(rule.actions.set_var_uwsgi_appid('myapp'), subject=None),
    ]))

    assert_lines([
        'route-run = setuser:iam',

    ], Section().routing.register_route([
        rule(rule.actions.set_var_remote_user('iam'), subject=None),
    ]))

    assert_lines(
        'route-run = harakiri:30',
        Section().routing.register_route(rule(rule.actions.set_harakiri(30), subject=None))
    )

    assert_lines(
        'route-run = sethome:/there',
        Section().routing.register_route(rule(rule.actions.set_var_uwsgi_home('/there'), subject=None))
    )

    assert_lines(
        'route-run = setscheme:uwsgi',
        Section().routing.register_route(rule(rule.actions.set_var_uwsgi_scheme('uwsgi'), subject=None))
    )

    assert_lines(
        'route-run = setscriptname:my.php',
        Section().routing.register_route(rule(rule.actions.set_var_script_name('my.php'), subject=None))
    )

    assert_lines(
        'route-run = setmethod:POST',
        Section().routing.register_route(rule(rule.actions.set_var_request_method('POST'), subject=None))
    )

    assert_lines(
        'route-run = seturi:http://there',
        Section().routing.register_route(rule(rule.actions.set_var_request_uri('http://there'), subject=None))
    )

    assert_lines(
        'route-run = setremoteaddr:127.0.0.1',
        Section().routing.register_route(rule(rule.actions.set_var_remote_addr('127.0.0.1'), subject=None))
    )

    assert_lines(
        'route-run = setpathinfo:/there/here.html',
        Section().routing.register_route(rule(rule.actions.set_var_path_info('/there/here.html'), subject=None))
    )

    assert_lines(
        'route-run = fixpathinfo:',
        Section().routing.register_route(
            rule(rule.actions.fix_var_path_info(), subject=None)
        )
    )

    assert_lines(
        'route-run = setfile:/var/uwsgi/app002.py',
        Section().routing.register_route(rule(rule.actions.set_script_file('/var/uwsgi/app002.py'), subject=None))
    )

    assert_lines(
        'route-run = setdocroot:/var/here',
        Section().routing.register_route(rule(rule.actions.set_var_document_root('/var/here'), subject=None))
    )

    assert_lines(
        'route-run = setprocname:myproc',
        Section().routing.register_route(rule(rule.actions.set_uwsgi_process_name('myproc'), subject=None))
    )

    uwsgi = rule.vars.uwsgi
    assert_lines(
        'route-run = alarm:pippo ${uwsgi[wid]} ${uwsgi[pid]}',
        Section().routing.register_route(rule(
            rule.actions.alarm('pippo', '%s %s' % (uwsgi('wid'), uwsgi('pid'))), subject=None
        ))
    )


def test_routing_goto_label(assert_lines):

    rule = Section.routing.route_rule
    actions = rule.actions
    subjects = rule.subjects

    label = 'localhost'

    assert_lines([
            'route-host = ^localhost$ goto:localhost',

            'route-label = localhost',
            'plugin = router_redirect',
            'route-user-agent = .*curl.* redirect-302:http://uwsgi.it',
            'route = (.*) continue:',
        ],

        Section().routing.register_route(

            rule(
                actions.do_goto(label),
                subjects.http_host('^localhost$')
            )

        ).routing.register_route(
            [
                rule(
                    actions.redirect('http://uwsgi.it'),
                    subjects.http_user_agent('.*curl.*')
                ),
                rule(
                    actions.do_continue(),
                    subjects.path_info('(.*)')
                ),
            ], label=label)
    )

