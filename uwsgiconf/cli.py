import sys
from contextlib import contextmanager

import click

from uwsgiconf import VERSION
from uwsgiconf.utils import ConfModule
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
def run(conf):
    """Runs uWSGI passing to it using the default or another `uwsgiconf` configuration module.

    """
    with errorprint():
        config = ConfModule(conf)
        config.spawn_uwsgi()


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


def main():
    """
    CLI entry point
    """
    base(obj={})


if __name__ == '__main__':
    main()
