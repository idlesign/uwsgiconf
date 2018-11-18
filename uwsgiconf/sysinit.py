from os import getuid, getgid
from os.path import dirname, basename, abspath
from textwrap import dedent

from .utils import get_output, Finder, UwsgiRunner


TYPE_UPSTART = 'upstart'
TYPE_SYSTEMD = 'systemd'

TYPES = [
    TYPE_UPSTART,
    TYPE_SYSTEMD,
]


def get_tpl_systemd():
    """

    Some Systemd hints:

        * uwsgiconf sysinit > my.service
        * sudo cp my.service /etc/systemd/system/my.service

        * sudo systemctl daemon-reload & sudo systemctl start my.service

        * journalctl -fu my.service

    """
    tpl = '''
        # Place into:   /etc/systemd/system/{project}.service
        # Start:        systemctl start {project}.service
        # Stop:         systemctl stop {project}.service
        # Restart:      systemctl restart {project}.service
        # Status:       systemctl status {project}.service

        [Unit]
        Description={project} uWSGI Service
        After=syslog.target

        [Service]
        #User=%(user)s
        #Group=%(group)s
        Environment="PATH=%(path)s"
        ExecStart={command}
        Restart=on-failure
        KillSignal=SIGTERM
        Type=notify
        StandardError=syslog
        NotifyAccess=all
        %(runtime_dir)s

        [Install]
        WantedBy=multi-user.target
    '''

    _, _, version = get_output(
        'systemd', ['--version']
    ).splitlines()[0].strip().partition(' ')

    runtime_dir = ''

    if version and int(version) >= 211:
        runtime_dir = 'RuntimeDirectory={project}'

    tpl = tpl % {
        'runtime_dir': runtime_dir,
        'path': UwsgiRunner.get_env_path(),
        'user': getuid(),
        'group': getgid(),
    }

    return tpl


def get_tpl_upstart():

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
        exec {command}
    '''

    tpl = tpl % {
        'path': UwsgiRunner.get_env_path(),
    }

    return tpl


TEMPLATES = {
    TYPE_SYSTEMD: get_tpl_systemd,
    TYPE_UPSTART: get_tpl_upstart,
}


def get_config(systype, conf_file, project):
    """Returns init system configuration file contents.

    :param str|unicode systype: System type alias, e.g. systemd, upstart
    :param str|unicode conf_file: Configuration file path.
    :param str|unicode project: Project name to use as service alias.
    :rtype: str|unicode

    """
    tpl = dedent(TEMPLATES.get(systype)()).strip()
    conf_file = abspath(conf_file)

    formatted = tpl.format(
        project=project or basename(dirname(conf_file)),
        command='%s run %s' % (Finder.uwsgiconf(), conf_file),
    )

    return formatted
