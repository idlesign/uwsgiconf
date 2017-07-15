import sys


def main():
    from uwsgiconf import VERSION

    print('uwsgiconf v%s' % ('.'.join(map(str, VERSION))))
    print('This CLI will evolve some day. Stay tuned.')

    sys.exit(1)
