#! /usr/bin/env python

if __name__ == "__main__":
    from django.conf import global_settings, settings
    from django.core.management import execute_from_command_line

    apps = global_settings.INSTALLED_APPS
    apps.append('uwsgiconf.contrib.django.uwsgify')

    settings.configure(INSTALLED_APPS=apps)

    execute_from_command_line(['makemigrations.py', 'makemigrations'])
