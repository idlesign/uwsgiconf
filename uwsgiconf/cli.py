import sys
from contextlib import contextmanager

import click

from uwsgiconf import VERSION
from uwsgiconf.utils import ConfModule, UwsgiRunner
from uwsgiconf.exceptions import ConfigurationError


@contextmanager
def errorprint():
    """Print out descriptions from ConfigurationError."""
    try:
        yield

    except ConfigurationError as e:
        click.secho('%s' % e, err=True, fg='red')
        sys.exit(1)


@click.group()
@click.version_option(version='.'.join(map(str, VERSION)))
def base():
    """uwsgiconf command line utility.

    Tools to facilitate uWSGI configuration.

    """

arg_conf = click.argument(
    'conf', type=click.Path(exists=True, dir_okay=False), default=ConfModule.default_name)


@base.command()
@arg_conf
@click.option('--only', help='Configuration alias from module to run uWSGI with.')
def run(conf, only):
    """Runs uWSGI passing to it using the default or another `uwsgiconf` configuration module.

    """
    with errorprint():
        config = ConfModule(conf)
        spawned = config.spawn_uwsgi(only)

        for alias, pid in spawned:
            click.secho("Spawned uWSGI for configuration aliased '%s'. PID %s" % (alias, pid), fg='green')


@base.command()
@arg_conf
def compile(conf):
    """Compiles classic uWSGI configuration file using the default
    or given `uwsgiconf` configuration module.

    """
    with errorprint():
        config = ConfModule(conf)
        for conf in config.configurations:
            conf.format(do_print=True)


@base.command()
def probe_plugins():
    """Runs uWSGI to determine what plugins are available and prints them out.

    Generic plugins come first then after blank line follow request plugins.

    """
    plugins = UwsgiRunner().get_plugins()

    for plugin in sorted(plugins.generic):
        click.secho(plugin)

    click.secho('')

    for plugin in sorted(plugins.request):
        click.secho(plugin)


def main():
    """
    CLI entry point
    """
    base(obj={})


if __name__ == '__main__':
    main()
