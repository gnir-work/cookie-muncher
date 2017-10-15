"""
A basic scrapper which receives a domain name and returns all of the links in the domain.
"""
import argparse
from datetime import datetime as dt
from cookieMuncher.spiders.cookie_muncher import crawl
import os
from urllib.parse import urlparse

from utils import check_directory_exists, OUTPUT_FIXTURE, LOG_FIXTURE

DEFAULT_DEPTH = 3
DEFAULT_LOG_FOLDER = "logs"
DEFAULT_OUTPUT_FOLDER = "output"

DEFAULT_DELAY = 0


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
    parser.add_argument('-d', '--domains', dest='domains', type=str,
                        help='The domains which the crawler should crawl, if given several domains '
                             'separated by space the crawler will crawl them all (Note that in case of several domains '
                             'the arguments need to be surrounded by "").',
                        required=True)
    parser.add_argument('-s', '--silent', dest='silent',
                        help='Will not log the crawling process if the flag is present.',
                        action='store_true')
    parser.add_argument('--log-file', dest='log_file', type=str, default=None, nargs='?', const='',
                        help="The folder to which the logs will be saved to, if the flag is present but empty "
                             "the logs will be saved to a file with the following name: [datetime] [net locations of domains given].log. "
                             "If the flag isn't present the log will be printed to stdout"
                        )
    parser.add_argument('--output-file', dest='output_file', type=str, default=None,
                        help="If the flag is present than the output of the crawl will be written to the filename "
                             "given in the path, otherwise the output will be written to a file with the following name "
                             "[datetime] [net locations of domains given].csv")
    parser.add_argument('--logs-folder', dest='logs_folder', type=str, default=DEFAULT_LOG_FOLDER,
                        help="If the flag is present than the logs from the crawl will be saved in the path "
                             "given in the argument, otherwise the logs will be saved in the logs folder in the "
                             "current directory")
    parser.add_argument('--output-folder', dest='output_folder', type=str, default=DEFAULT_OUTPUT_FOLDER,
                        help="If the flag is present than the output from the crawl will be saved in the path "
                             "given in the argument, otherwise the output will be saved in the output folder in the "
                             "current directory")
    parser.add_argument('--delay', dest='delay', type=float, default=DEFAULT_DELAY,
                        help="Set the delay between each request of the crawler, The input is in SECONDS. for example --delay 0.25. "
                             "Default the delay is set to 0.")
    parser.add_argument('--user-agent', dest='user_agent', type=str, default=None,
                        help="Set hardcoded the user agent that the crawler will use, by default the crawler sets a random user agent "
                             "from a predefined list of user agents (There is no check if the user agent is valid!).")
    return parser


def generate_file_name(folder, domains, fixture):
    """
    Creates the file name from the folder and domains that the crawler will crawl.
    the file name will be: [datetime] [net locations of domains given].[fixture]
    :param folder: The folder where the file we be saved
    :param domains: The domains the crawler will crawl.
    :param fixture: The fixture of the file.
    :return: The full path to the file.
    """
    return os.path.join(folder,
                        "{} {}.{}".format(str(dt.now()).replace(':', '.'), generate_netlocations_from_domains(domains),
                                          fixture))


def generate_netlocations_from_domains(domains):
    return list({urlparse(domain).netloc for domain in domains.split()})


def format_arguments(args):
    """
    Formats the arguments given to the script.
    :param args: The args given to the script.
    :return: The formatted args.
    """
    allowed_domains = []
    if args.domain_only:
        allowed_domains = generate_netlocations_from_domains(args.domains)
    args.output_file = args.output_file or generate_file_name(args.output_folder, args.domains, OUTPUT_FIXTURE)
    if args.silent:
        args.log_file = None
    if args.log_file == '':
        args.log_file = generate_file_name(args.logs_folder, args.domains, LOG_FIXTURE)
    args.domains = args.domains.split()
    check_directory_exists(args.logs_folder)
    check_directory_exists(args.output_folder)
    return args, allowed_domains


def run(parser):
    """
    Creates the crawler using the parser to parse the cli arguments.
    :param parser: A configured instance of argsParser
    :return: A configured crawler instance.
    """
    args, allowed_domains = format_arguments(parser.parse_args())
    crawl(args.domains, allowed_domains, args.depth, args.silent, args.log_file, args.output_file, args.delay,
          args.user_agent)


if __name__ == '__main__':
    parser = create_parser()
    run(parser)
