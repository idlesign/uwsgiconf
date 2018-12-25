from os.path import dirname, basename, abspath
from textwrap import dedent

from .config import Configuration
from .utils import Finder, UwsgiRunner

if False:  # pragma: nocover
    from .config import Section


TYPE_UPSTART = 'upstart'
TYPE_SYSTEMD = 'systemd'

TYPES = [
    TYPE_UPSTART,
    TYPE_SYSTEMD,
]


def get_tpl_systemd(conf):
    """

    Some Systemd hints:

        * uwsgiconf sysinit > my.service
        * sudo cp my.service /etc/systemd/system/

        * sudo sh -c "systemctl daemon-reload; systemctl start my.service"

        * journalctl -fu my.service

    :param Section conf: Section object.
    :rtype: str|unicode

    """
    tpl = '''
        # Place into:   /etc/systemd/system/{project}.service
        # Setup:        sudo sh -c "systemctl daemon-reload; systemctl start {project}.service"
        # Start:        systemctl start {project}.service
        # Stop:         systemctl stop {project}.service
        # Restart:      systemctl restart {project}.service
        # Status:       systemctl status {project}.service
        # Journal:      journalctl -fu {project}.service

        [Unit]
        Description={project} uWSGI Service
        After=syslog.target

        [Service]
        Environment="PATH=%(path)s"
        ExecStartPre=-/bin/install -d -m 0755 -o %(user)s -g %(group)s %(runtime_dir)s
        ExecStart={command}
        Restart=on-failure
        KillSignal=SIGTERM
        Type=notify
        StandardError=syslog
        NotifyAccess=all

        [Install]
        WantedBy=multi-user.target
    '''
    # We do not use 'RuntimeDirectory' systemd directive since we need to chown.

    uid, gid = conf.main_process.get_owner()

    tpl = tpl % {
        'runtime_dir': conf.replace_placeholders('{project_runtime_dir}'),
        'path': UwsgiRunner.get_env_path(),
        'user':  uid,
        'group': gid,
    }

    return tpl


def get_tpl_upstart(conf):
    """

    :param Section conf: Section object.
    :rtype: str|unicode

    """
    tpl = '''
        # Place into: /etc/init/{project}.conf
        # Verify:     initctl check-config {project}
        # Start:      initctl start {project}
        # Stop:       initctl stop {project}
        # Restart:    initctl restart {project}
        
        description "{project} uWSGI Service"
        start on runlevel [2345]
        stop on runlevel [06]
        
        respawn
        
        env PATH=%(path)s
        pre-start exec -/bin/install -d -m 0755 -o %(user)s -g %(group)s %(runtime_dir)s
        
        exec {command}
    '''

    uid, gid = conf.main_process.get_owner()

    tpl = tpl % {
        'path': UwsgiRunner.get_env_path(),
        'runtime_dir': conf.replace_placeholders('{project_runtime_dir}'),
        'user': uid,
        'group': gid,
    }

    return tpl


TEMPLATES = {
    TYPE_SYSTEMD: get_tpl_systemd,
    TYPE_UPSTART: get_tpl_upstart,
}


def get_config(systype, conf, conf_path, runner=None, project_name=None):
    """Returns init system configuration file contents.

    :param str|unicode systype: System type alias, e.g. systemd, upstart
    :param Section|Configuration conf: Configuration/Section object.
    :param str|unicode conf_path: File path to a configuration file or a command producing such a configuration.
    :param str|unicode runner: Runner command to execute conf_path. Defaults to ``uwsgiconf`` runner.
    :param str|unicode project_name: Project name to override.
    :rtype: str|unicode

    """
    runner = runner or ('%s run' % Finder.uwsgiconf())
    conf_path = abspath(conf_path)

    if isinstance(conf, Configuration):
        conf = conf.sections[0]  # todo Maybe something more intelligent.

    tpl = dedent(TEMPLATES.get(systype)(conf=conf))

    formatted = tpl.strip().format(
        project=project_name or conf.project_name or basename(dirname(conf_path)),
        command='%s %s' % (runner, conf_path),
    )

    return formatted
