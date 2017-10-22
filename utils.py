import argparse
import json
import os
from urllib.parse import urlparse

from db import CookieInfo

OUTPUT_FIXTURE = 'csv'
LOG_FIXTURE = 'log'


def check_directory_exists(path):
    """
    Checks if the path exists, if it doesn't creates it.
    :param path: The path to be checked.
    """
    if not os.path.exists(path):
        os.makedirs(path)


def enrich_cookie(cookie, session):
    cookie_json = json.loads(cookie.cookie_attr)
    cookie_info = session.query(CookieInfo).filter(CookieInfo.id == cookie.cookie_info_id).scalar()
    cookie_json['about'] = cookie_info.about
    cookie_json['purpose'] = cookie_info.purpose
    cookie_json['extraction_time'] = cookie.datetime
    return cookie_json


def create_parser():
    """
    Creates the parser with all of the expected arguments.
    :return: The configured parser instance.
    """
    parser = argparse.ArgumentParser(description="A web scrapping cli tool")
    parser.add_argument('-i', '--id', dest='id', type=int, help='The id of the MuncherSchedule.')
    return parser


def find_depth_of_url(url):
    """
    Returns the depth of the url, for example https://tumblr.com/ is depth 0
    :param url: The url to be checked
    :return: The depth
    """
    return len([p for p in urlparse(url).path.split('/') if p])


def update_first_found_url(cookie, new_url):
    """
    Updates the first found url in case the new url is of a smaller depth than the current one.
    :param cookie: The cookie as it is saved in the db
    :param new_url: The new url in which the cookie was found
    """
    if find_depth_of_url(new_url) < find_depth_of_url(cookie['first_found_url']):
        cookie['first_found_url'] = new_url
