import argparse
import json
import os
import datetime
import requests
from bs4 import BeautifulSoup as Soup
import sys

from dotmap import DotMap
from sqlalchemy import exists
from sqlalchemy.orm import Session

from db import engine, MuncherSchedule, MuncherConfig, UrlScans, Cookies, ExtractedCookies, CookieInfo, MuncherStats
from utils import LOG_FIXTURE, check_directory_exists
from selenium import webdriver

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

session = Session(engine)


def create_parser():
    """
    Creates the parser with all of the expected arguments.
    :return: The configured parser instance.
    """
    parser = argparse.ArgumentParser(description="A Cookie collection tool. ")
    parser.add_argument('-i', '--id', dest='id', required=True, type=int,
                        help="The id of the MuncherSchedule.")
    parser.add_argument('--os', dest='os', type=str, default='linux_64',
                        choices=['linux_64', 'linux_32', 'mac', 'windows'],
                        help="Choose which operation system the script will run "
                             "(this is relevant for the headless browser driver).")

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


def format_arguments(args, os_system):
    """
    Formats the arguments given to the script.
    :param args: The args given to the script.
    :return: The formatted args.
    """
    if args.silent:
        args.log_file = os.devnull
    elif args.log_file == '':
        args.log_file = generate_file_name(args.logs_folder, args.input_file, LOG_FIXTURE)
    check_directory_exists(args.logs_folder)
    driver_path = os.path.join(DRIVER_FOLDER, DRIVER_NAMES[os_system])
    return args, driver_path


def scrap_cookie(cookie, url):
    """
    Scrape the https://cookiepedia.co.uk website for information on the specific cookie
    :param cookie: The json cookie retrieved using phantomJs.
    :param url: The url from which the cookie was loaded.
    :return: The id of the item created in the db for the cookie.
    """
    about = None
    purpose = None
    page_content = requests.get(COOKIEPEDIA_PATH_FORMAT.format(cookie['name']), verify=False).content
    soup = Soup(page_content, SOUP_PARSER)
    if soup.find('h2').text == FOUND_COOKIE_H2:
        paragraphs = soup.find('div', attrs={'id': 'content-left'}).find_all('p')
        about = paragraphs[0].text
        purpose = paragraphs[1].find('strong').text
    info = CookieInfo(cookie_name=cookie['name'], purpose=purpose, about=about,
                      datetime=datetime.datetime.now())
    session.add(info)
    session.commit()
    return info.id


def handle_cookie(cookie, url):
    """
    Returns information about the specific cookie as found in https://cookiepedia.co.uk either from cache or from
    the scarping the site.
    :param UrlScans url: The url item in the db.
    :param cookie: The json cookie retrieved using phantomJs.
    :return:about and purpose information about the cookie.
    """
    if session.query(exists().where(CookieInfo.cookie_name == cookie['name'])).scalar():
        cookie_info_id = session.query(CookieInfo).filter(CookieInfo.cookie_name == cookie['name']).scalar().id
    else:
        cookie_info_id = scrap_cookie(cookie, url)
    cookie_midal = Cookies(cookie_info_id=cookie_info_id, cookie_source=0, cookie_attr=json.dumps(cookie),
                     datetime=datetime.datetime.now())
    session.add(cookie_midal)
    session.commit()
    return cookie_midal.id


def handle_url(url, driver):
    """
    Retrieves the cookies from the url.
    :param UrlScans url: The url item in the db.
    :param driver: The headless browser driver
    :return:
    """
    print("getting url")
    driver.get(url.url)
    print("done")
    for cookie in driver.get_cookies():
        cookie_id = handle_cookie(cookie, url.url)
        session.add(ExtractedCookies(url_id=url.id, cookie_id=cookie_id))


def loading_bar(done, total):
    """
    Print how much of the cookie gathering is done.
    :param done: How much urls have been checked
    :param total: How much urls were read from the file
    """
    sys.stdout.write("\rCookie extracting: %d%%" % int((done / float(total) * 100)))
    sys.stdout.flush()


def handle_input(rows, schedule_id, driver):
    """
    Handle all of the rows that were retrieved from the db.
    :param rows: The rows retrieved from the db.
    :param schedule_id: the id of the scheduled tastblCookie_Infok.
    :param driver: The phantomJS driver for extracting the cookies.

    """
    done = 1
    total = len(rows)
    print("Starting cookie extraction on {} urls...".format(total))
    sys.stdout.write("\rCookie extracting: 0%")
    for row in rows:
        handle_url(row, driver)
        loading_bar(done, total)
        done += 1


def run(schedule_id, args, driver_path):
    """
    Read the urls from the urls table with the given schedule id and find the cookies for each url .
    :param schedule_id: The scheduled task id.
    :param args: The args from the config table.
    :param driver_path: the path to the driver.
    """
    args.log_file = 'a.log'
    driver = webdriver.PhantomJS(executable_path=driver_path, service_log_path=args.log_file)
    rows = session.query(UrlScans).filter(UrlScans.schedule_id == schedule_id).all()
    handle_input(rows, schedule_id, driver)
    session.commit()
    driver.quit()


def main():
    parser = create_parser()
    # parser_args = parser.parse_args()
    schedule = session.query(MuncherSchedule).get(1)
    config = session.query(MuncherConfig).get(schedule.config_id)
    args, driver_path = format_arguments(DotMap(json.loads(config.json_params)), 'linux_64')
    run(1, args, driver_path)


if __name__ == '__main__':
    main()
