"""
A basic scrapper which receives a domain
"""
import argparse
from cookieMuncher.spiders.cookie_muncher import crawl
DEFAULT_DEPTH = 3


def create_parser():
    """
    Creates the parser with all of the expected arguments.
    :return: The configured parser instance.
    """
    parser = argparse.ArgumentParser(description="A web scrapping cli tool")
    parser.add_argument('--domain-only', dest='domain_only',
                        help='Searches only links from the current domain if flag is present', action='store_true')
    parser.add_argument('-n', '--depth', dest='depth', type=int, help="The depth for which the crawler should crawl.",
                        default=DEFAULT_DEPTH)
    parser.add_argument('-d', '--domain', dest='domain', type=str, help="The domain which the crawler should crawl", required=True)
    return parser

def run(parser):
    """
    Creates the crawler using the parser to parse the cli arguments.
    :param parser: A configured instance of argsParser
    :return: A configured crawler instance.
    """
    args = parser.parse_args()
    crawl(args.domain, args.domain_only, args.depth)

if __name__ == '__main__':
    parser = create_parser()
    run(parser)