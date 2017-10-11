"""
A basic scrapper which receives a domain
"""
import argparse
from datetime import datetime as dt
import uuid
from cookieMuncher.spiders.cookie_muncher import crawl
import os

DEFAULT_DEPTH = 3
DEFAULT_LOG_FOLDER = "logs"
DEFAULT_OUTPUT_FOLDER = "output"


def create_parser():
    """
    Creates the parser with all of the expected arguments.
    :return: The configured parser instance.
    """
    parser = argparse.ArgumentParser(description="A web scrapping cli tool")
    parser.add_argument('--domain-only', dest='domain_only',
                        help='Searches only links from the current domain if flag is present', action='store_true')
    parser.add_argument('-n', '--depth', dest='depth', type=int, help='The depth for which the crawler should crawl.',
                        default=DEFAULT_DEPTH)
    parser.add_argument('-d', '--domain', dest='domain', type=str, help='The domain which the crawler should crawl',
                        required=True)
    parser.add_argument('-s', '--silent', dest='silent',
                        help='Will not log the crawling process if the flag is present.',
                        action='store_true')
    parser.add_argument('--log-file', dest='log_file', type=str, default=None, nargs='?', const='',
                        help="The folder to which the logs will be saved to, if the flag is present but empty "
                             "the logs will be saved to a file with the following name: [datetime]-[random id].log"
                             "If the flag isn't present the log will be printed to stdout"
                        )
    parser.add_argument('--output-file', dest='output_file', type=str, default=None,
                        help="If the flag is present than the output of the crawl will be written to the filename "
                             "given in the path, otherwise the output will be written to a file with the following name"
                             "[datetime]-[random id].csv")
    parser.add_argument('--logs-folder', dest='logs_folder', type=str, default=DEFAULT_LOG_FOLDER,
                        help="If the flag is present than the logs from the crawl will be saved in the path"
                             "given in the argument, otherwise the logs will be saved in the logs folder in the "
                             "current directory")
    parser.add_argument('--output-folder', dest='output_folder', type=str, default=DEFAULT_OUTPUT_FOLDER,
                        help="If the flag is present than the output from the crawl will be saved in the path"
                             "given in the argument, otherwise the output will be saved in the output folder in the "
                             "current directory")
    return parser


def check_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def format_arguments(args):
    print args
    if args.output_file is None:
        args.output_file = os.path.join(args.output_folder,
                                        "{} {}.csv".format(str(dt.now()).replace(':', '.'), uuid.uuid4().get_hex()))
    if args.silent:
        args.log_file = None
    if args.log_file == '':
        args.log_file = os.path.join(args.logs_folder,
                                     "{} {}.log".format(str(dt.now()).replace(':', '.'), uuid.uuid4().get_hex()))
    check_directory_exists(args.logs_folder)
    check_directory_exists(args.output_folder)
    return args


def run(parser):
    """
    Creates the crawler using the parser to parse the cli arguments.
    :param parser: A configured instance of argsParser
    :return: A configured crawler instance.
    """
    args = format_arguments(parser.parse_args())

    print args
    crawl(args.domain, args.domain_only, args.depth, args.silent, args.log_file, args.output_file)


if __name__ == '__main__':
    parser = create_parser()
    run(parser)
