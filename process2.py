import argparse
import os
import datetime

import sys

from utils import OUTPUT_FIXTURE, LOG_FIXTURE, check_directory_exists
from selenium import webdriver
import csv

DEFAULT_LOG_FOLDER = 'cookies_logs'
DEFAULT_OUTPUT_FOLDER = 'cookies_output'
OUTPUT_CSV_FILE_HEADERS = ['datetime', 'url', 'cookies']


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
        args.log_file = '/dev/null'
    elif args.log_file == '':
        args.log_file = generate_file_name(args.logs_folder, args.input_file, LOG_FIXTURE)
    check_directory_exists(args.logs_folder)
    check_directory_exists(args.output_folder)
    return args


def handle_url(url, writer, driver):
    """
    Retrieves the cookies from the url.
    """
    driver.get(url)
    writer.writerow([datetime.datetime.now(), url, driver.get_cookies()])


def read_input_file(input_file):
    """
    Read the input file and extract the rows in the files
    :param input_file: The path to the file.
    :return: An array of [url, datetime].
    """
    with open(args.input_file, 'rb') as urls_file:
        reader = csv.reader(urls_file)
        rows = list(reader)[1:]
        return rows


def loading_bar(done, total):
    """
    Print how much of the cookie gathering is done.
    :param done: How much urls have been checked
    :param total: How much urls were read from the file
    """
    sys.stdout.write("\rCookie extracting: %d%%" % int((done / float(total) * 100)))
    sys.stdout.flush()


def handle_input(rows, writer, driver):
    """
    Handle all of the rows that were retrieved from the input file.
    :param rows: The rows retrieved from the input file.
    :param writer: The csv writer.
    :param driver: The phantomJS driver for extracting the cookies.
    """
    done = 1
    total = len(rows)
    print "Starting cooking extraction on {} urls...".format(total)
    for url, _ in rows:
        handle_url(url, writer, driver)
        loading_bar(done, total)
        done += 1


def run(args):
    """
    Read the input file given in the args and find the cookies for each url in the file.
    :param args: The args given to the process.
    """
    driver = webdriver.PhantomJS(executable_path='./phantomjs', service_log_path=args.log_file)
    rows = read_input_file(args.input_file)
    with open(args.output_file, 'wb') as output:
        writer = csv.writer(output)
        writer.writerow(OUTPUT_CSV_FILE_HEADERS)
        handle_input(rows, writer, driver)
    driver.quit()


if __name__ == '__main__':
    parser = create_parser()
    args = format_arguments(parser.parse_args())
    run(args)
