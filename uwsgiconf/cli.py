import sys
import argparse


def main():
    from uwsgiconf import VERSION

    arg_parser = argparse.ArgumentParser(prog='uwsgiconf', description='Configure uWSGI from your Python code')
    arg_parser.add_argument('--version', action='version', version='.'.join(map(str, VERSION)))

    arg_parser.add_argument('arg1', help='arg1 help')
    arg_parser.add_argument('--opt', help='optional arg help', action='store_true', default=False)

    # subparsers = arg_parser.add_subparsers(dest='my_subparsers')
    # subcommand_parser = subparsers.add_parser('subcommand', help='subcommand help')

    parsed_args = arg_parser.parse_args()
    # parsed_args = vars(parsed_args)  # Convert args to dict
    # subparsed_args = parsed_args['subparsers']

    # Logic goes here.
    # if parsed_args['opt']:

    sys.exit(1)

