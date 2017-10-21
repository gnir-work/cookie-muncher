import argparse

import datetime
import json

from sqlalchemy.orm import Session

from db import MuncherSchedule, UrlScans, ExtractedCookies, Cookies, engine, CookieInfo
from csv import writer

from extractor import Extractor
from utils import enrich_cookie, create_parser

ROW_HEADERS = ['url', 'extraction time', 'name', 'purpose', 'about', 'domain', 'http only', 'secure', 'value',
               'expiration date']


class UrlData(object):
    def __init__(self, url, session):
        self.url = url
        self.session = session
        self.cookies = []

    def load_cookie_data(self):
        extracted_cookies = self.session.query(ExtractedCookies).filter(ExtractedCookies.url_id == self.url.id).all()
        cookies = [self.session.query(Cookies).get(extracted_cookie.cookie_id) for extracted_cookie in
                   extracted_cookies]
        cookie_jsons = [enrich_cookie(cookie, self.session) for cookie in cookies]
        self.cookies = cookie_jsons

    def write_to_csv(self, csv_writer):
        """

        :param csv.writer csv_writer:
        :return:
        """
        for cookie in self.cookies:
            csv_writer.writerow(self._create_row_for_csv(cookie))

    def _create_row_for_csv(self, cookie):
        return [self.url.url, cookie['extraction_time'], cookie['name'], cookie['purpose'], cookie['about'],
                cookie['domain'], cookie['httponly'], cookie['secure'],
                cookie['value'], cookie['expires']]



class CsvExtractor(Extractor):
    def __init__(self, schedule_id):
        super(CsvExtractor, self).__init__(schedule_id)
        self._csv_writer = None
        self._output_file = None
        self._output_file_name = None
        self._urls = None

    def extract(self):
        self.csv_writer.writerow(ROW_HEADERS)
        for url in self.urls:
            print("writing {} to {}".format(url.url, self._output_file_name))
            row = UrlData(url, self.session)
            row.load_cookie_data()
            row.write_to_csv(self.csv_writer)

    @property
    def csv_writer(self):
        if not self._csv_writer:
            self._output_file = open(self.output_file_name, 'w')
            self._csv_writer = writer(self._output_file)
        return self._csv_writer

    @property
    def output_file_name(self):
        if not self._output_file_name:
            self._output_file_name = "{} {}".format(self.schedule.title, datetime.datetime.now())
        return self._output_file_name

    @property
    def urls(self):
        if self._urls is None:
            self._urls = self.session.query(UrlScans).filter(UrlScans.schedule_id == self.schedule.id)
        return self._urls

    def close(self):
        self._csv_writer = None
        self._output_file.close()


def main():
    parser = create_parser()
    id = parser.parse_args().id
    extractor = CsvExtractor(schedule_id=id)
    extractor.extract()


if __name__ == '__main__':
    main()
