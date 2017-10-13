import argparse
import os
import datetime
import requests
from bs4 import BeautifulSoup as Soup
import sys
from utils import OUTPUT_FIXTURE, LOG_FIXTURE, check_directory_exists
from selenium import webdriver
import csv

# Remove annoying warning message when accessing https://cookiepedia.co.uk because of their broken
# certificate.
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEFAULT_LOG_FOLDER = 'cookies_logs'
DEFAULT_OUTPUT_FOLDER = 'cookies_output'
OUTPUT_CSV_FILE_HEADERS = ['datetime', 'url', 'cookies', 'about', 'purpose']
DRIVER_FOLDER = os.path.join('.', 'drivers')
DRIVER_NAMES = {
    'windows': 'windows_phantom.exe',
    'linux_64': 'linux_64_phantom',
    'linux_32': 'linux_32_phantom',
    'mac': 'mac_phantom'
}
SOUP_PARSER = 'html.parser'
COOKIEPEDIA_PATH_FORMAT = 'https://cookiepedia.co.uk/cookies/{}'
FOUND_COOKIE_H2 = 'About this cookie:'
CACHE = dict()


def create_parser():
    """
    Creates the parser with all of the expected arguments.
    :return: The configured parser instance.
    """
    parser = argparse.ArgumentParser(description="A Cookie collection tool. ")
    parser.add_argument('-i', '--input-file', dest='input_file', required=True,
                        help="The path to the file that contains the output of process1.py script.")
    parser.add_argument('-s', '--silent', dest='silent',
                        help='Will not log the cookie gathering process if the flag is present.',
                        action='store_true')
    parser.add_argument('--log-file', dest='log_file', type=str, default='', nargs='?', const='',
                        help="The folder to which the logs will be saved to, if the flag isn't"
                             " or empty present but empty "
                             "the logs will be saved to a file with the following name: cookies_[input file].log. "
                        )
    parser.add_argument('--output-file', dest='output_file', type=str, default=None,
                        help="If the flag is present than the output of the cookie"
                             " gathering will be written to the filename "
                             "given in the path, otherwise the output will"
                             " be written to a file with the following name "
                             "cookies_[input_file].csv")
    parser.add_argument('--logs-folder', dest='logs_folder', type=str, default=DEFAULT_LOG_FOLDER,
                        help="If the flag is present than the logs from the cookie gathering will be saved in the path "
                             "given in the argument, otherwise the logs will be saved in "
                             "the cookies_logs folder in the "
                             "current directory")
    parser.add_argument('--output-folder', dest='output_folder', type=str, default=DEFAULT_OUTPUT_FOLDER,
                        help="If the flag is present than the output from the cookie "
                             "gathering will be saved in the path "
                             "given in the argument, otherwise the output will be saved in "
                             "the cookies_output folder in the "
                             "current directory")
    parser.add_argument('--os', dest='os', type=str, default='linux_64',
                        choices=['linux_64', 'linux_32', 'mac', 'windows'],
                        help="Choose which operation system the script will run (this is relevant for the headless browser driver). "
                             "The default is linux 64.")
    parser.add_argument('--cache', dest='cache', action='store_true',
                        help='If this flag is present cache the cookie information found for cookies on '
                             'https://cookiepedia.co.uk/cookies for the next the time that cookie is encountered. '
                             "Doesn't cache cookies that weren't found on the site")
    return parser


def generate_file_name(folder, input_file, extension):
    """
    Creates the file name from the folder and domains that the crawler will crawl.
    the file name will be: [datetime] [net locations of domains given].[fixture]
    :param extension: The extension of the file.
    :param input_file: The path to the input file.
    :param folder: The folder where the file we be saved
    :return: The full path to the file.
    """
    return os.path.join(folder, "cookies_{}.{}".format(os.path.splitext(os.path.basename(input_file))[0], extension))


def format_arguments(args):
    """
    Formats the arguments given to the script.
    :param args: The args given to the script.
    :return: The formatted args.
    """
    if args.output_file is None:
        args.output_file = generate_file_name(args.output_folder, args.input_file, OUTPUT_FIXTURE)
    if args.silent:
        args.log_file = os.devnull
    elif args.log_file == '':
        args.log_file = generate_file_name(args.logs_folder, args.input_file, LOG_FIXTURE)
    check_directory_exists(args.logs_folder)
    check_directory_exists(args.output_folder)
    driver_path = os.path.join(DRIVER_FOLDER, DRIVER_NAMES[args.os])
    return args, driver_path


def handle_cookie(cookie, args):
    """
    Returns information about the specific cookie as found in https://cookiepedia.co.uk
    :param args: The args passed to the script
    :param cookie: The json cookie retrieved using phantomJs.
    :return:about and purpose information about the cookie.
    """
    about = None
    purpose = None
    if args.cache:
        if cookie['name'] in CACHE:
            about = CACHE[cookie['name']]['about']
            purpose = CACHE[cookie['name']]['purpose']
        else:
            page_content = requests.get(COOKIEPEDIA_PATH_FORMAT.format(cookie['name']), verify=False).content
            soup = Soup(page_content, SOUP_PARSER)
            if soup.find('h2').text == FOUND_COOKIE_H2:
                about, purpose = scrap_cookie(soup)
                CACHE[cookie['name']] = dict()
                CACHE[cookie['name']]['about'] = about
                CACHE[cookie['name']]['purpose'] = purpose
    else:
        page_content = requests.get(COOKIEPEDIA_PATH_FORMAT.format(cookie['name']), verify=False).content
        soup = Soup(page_content, SOUP_PARSER)
        about, purpose = scrap_cookie(soup)
    return about, purpose


def scrap_cookie(soup):
    """
    Scrape the https://cookiepedia.co.uk website for information on the specific cookie
    :param soup: BeautifulSoup instance already loaded with the html of the relevant page from the site.
    :return: about and purpose information for the cookie
    """
    paragraphs = soup.find('div', attrs={'id': 'content-left'}).find_all('p')
    about = paragraphs[0].text
    purpose = paragraphs[1].find('strong').text
    return about, purpose


def handle_url(url, writer, driver, args):
    """
    Retrieves the cookies from the url.
    """
    driver.get(url)
    for cookie in driver.get_cookies():
        about, purpose = handle_cookie(cookie, args)
        writer.writerow([datetime.datetime.now(), url, cookie, about, purpose])


def read_input_file(input_file):
    """
    Read the input file and extract the rows in the files
    :param input_file: The path to the file.
    :return: An array of [url, datetime].
    """
    with open(input_file) as urls_file:
        reader = csv.reader(urls_file)
        rows = list(reader)
        return rows


def loading_bar(done, total):
    """
    Print how much of the cookie gathering is done.
    :param done: How much urls have been checked
    :param total: How much urls were read from the file
    """
    sys.stdout.write("\rCookie extracting: %d%%" % int((done / float(total) * 100)))
    sys.stdout.flush()


def handle_input(rows, writer, driver, args):
    """
    Handle all of the rows that were retrieved from the input file.
    :param args: The arguments passed to the script
    :param rows: The rows retrieved from the input file.
    :param writer: The csv writer.
    :param driver: The phantomJS driver for extracting the cookies.
    """
    index = 1
    if rows[0][0] == 'link':
        index = 0
    rows = rows[1:]
    done = 1
    total = len(rows)
    print("Starting cooking extraction on {} urls...".format(total))
    for row in rows:
        handle_url(row[index], writer, driver, args)
        loading_bar(done, total)
        done += 1


def run(args, driver_path):
    """
    Read the input file given in the args and find the cookies for each url in the file.
    :param args: The args given to the process.
    :param driver_path: The path to the driver file.
    """
    driver = webdriver.PhantomJS(executable_path=driver_path, service_log_path=args.log_file)
    rows = read_input_file(args.input_file)
    with open(args.output_file, 'w') as output:
        writer = csv.writer(output)
        writer.writerow(OUTPUT_CSV_FILE_HEADERS)
        handle_input(rows, writer, driver, args)
    driver.quit()


if __name__ == '__main__':
    parser = create_parser()
    args, driver_path = format_arguments(parser.parse_args())
    run(args, driver_path)
