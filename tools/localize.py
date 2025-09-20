#! /usr/bin/env python

# NOTE: Run from project root.
if __name__ == "__main__":
    from django.conf import global_settings, settings
    from django.core.management import execute_from_command_line

    apps = global_settings.INSTALLED_APPS
    apps.append('uwsgiconf.contrib.django.uwsgify')

    settings.configure(INSTALLED_APPS=apps)

    execute_from_command_line([
        'localize.py', 'makemessages', '--locale=ru', '--symlinks', '--no-location', '--no-obsolete'
    ])
