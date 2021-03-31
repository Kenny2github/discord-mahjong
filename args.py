import argparse

parser = argparse.ArgumentParser(description='Run the bot.')
parser.add_argument('prefix', nargs='?', help='the bot prefix', default=';')
parser.add_argument('-v', action='store_true', default=False,
                    help='emit debugging log messages')
parser.add_argument('--stdout', action='store_true', default=False,
                    help='log to stdout instead of file')

cmdargs = parser.parse_args()