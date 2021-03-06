import json

import datetime
from jinja2 import Template

from db import UrlScans, ExtractedCookies, Cookies, MuncherConfig
from extractor import Extractor
from utils import enrich_cookie, update_first_found_url, create_parser

TEMPLATE_FILE_NAME = 'html_report_Gareth.html'
OUTPUT_FILE_TEMPLATE = '{} {}.html'

class CookiesInformation(object):
    def __init__(self, session):
        self.session = session
        self.cookies_by_type = {}
        self.cookies_count = 0

    def add_cookie(self, new_cookie, url):
        """
        Adds a cookie, in case the cookie doesn't exists creates one, in case it does exists updates its first found url.
        :param new_cookie: The new cookie to be added
        :param url: The url from which to cookie was extracted.
        """
        cookies = self.cookies_by_type.get(new_cookie['purpose'], [])
        old_cookie = [cookie for cookie in cookies if cookie['name'] == new_cookie['name']]
        if not old_cookie:
            new_cookie['first_found_url'] = url
            cookies.append(new_cookie)
            self.cookies_count += 1
        else:
            update_first_found_url(old_cookie[0], url)

        self.cookies_by_type[new_cookie['purpose']] = cookies

    @property
    def cookies(self):
        return [{'type': cookie_type, 'cookies': self.cookies_by_type[cookie_type]} for cookie_type in
                self.cookies_by_type.keys()]


class HtmlExtractor(Extractor):
    def __init__(self, schedule_id):
        super(HtmlExtractor, self).__init__(schedule_id)
        self.template_file_name = TEMPLATE_FILE_NAME
        self.cookies = CookiesInformation(self.session)
        self.config = json.loads(self.session.query(MuncherConfig).get(self.schedule.config_id).json_params)

    def generate_html(self):
        """
        Loads all of the extracted cookies to the jinja2 template file.
        """
        self._extract_cookies()
        with open(self.template_file_name) as template_file:
            template = Template(template_file.read())
            html = template.render(scan_date=self.schedule.start_datetime,
                                   domain_name=self.config['domains'],
                                   cookies_count=self.cookies.cookies_count,
                                   unidentified_cookies_count=len(self.cookies.cookies_by_type['Unknown']),
                                   cookies_by_types=self.cookies.cookies,
                                   scan_title=self.schedule.title,
                                   scan_description=self.schedule.description)
            with open(OUTPUT_FILE_TEMPLATE.format(self.schedule.title, datetime.datetime.now()), 'w') as output:
                output.write(html)

    def _extract_cookies(self):
        """
        Extracts all of the cookies and loads them to cookie container class.
        """
        urls = self.session.query(UrlScans).filter(UrlScans.schedule_id == self.schedule.id).all()
        for url in urls:
            print("extracting data for {}".format(url.url))
            extracted_cookies = self.session.query(ExtractedCookies).filter(ExtractedCookies.url_id == url.id).all()
            cookies = [self.session.query(Cookies).get(extracted_cookie.cookie_id) for extracted_cookie
                       in extracted_cookies]
            for cookie in cookies:
                self.cookies.add_cookie(enrich_cookie(cookie, self.session), url.url)


def main():
    id = create_parser().parse_args().id
    extractor = HtmlExtractor(id)
    extractor.generate_html()


if __name__ == '__main__':
    main()
