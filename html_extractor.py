import json

from jinja2 import Template
from sqlalchemy.orm import Session

from db import engine, MuncherSchedule, UrlScans, ExtractedCookies, Cookies, MuncherConfig
from extractor import Extractor
from utils import enrich_cookie

TEMPLATE_FILE_NAME = 'html_report.html'


class CookiesInformation(object):
    def __init__(self, session):
        self.session = session
        self.cookies_by_type = {}
        self.cookies_count = 0

    def add_cookie(self, new_cookie):
        cookies = self.cookies_by_type.get(new_cookie['purpose'], [])
        if not any([cookie['name'] == new_cookie['name'] for cookie in cookies]):
            cookies.append(new_cookie)
            self.cookies_count += 1
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
        self._extract_cookies()
        with open(self.template_file_name) as template_file:
            template = Template(template_file.read())
            html = template.render(scan_date=self.schedule.start_datetime,
                                   domain_name=self.config['domains'],
                                   cookies_count=self.cookies.cookies_count,
                                   unidentified_cookies_count=len(self.cookies.cookies_by_type['Unknown']),
                                   cookies_by_types=self.cookies.cookies,
                                   scan_title = self.schedule.title,
                                   scan_description = self.schedule.description)
            print self.cookies.cookies
            with open('test.html', 'w') as output:
                output.write(html)

    def _extract_cookies(self):
        urls = self.session.query(UrlScans).filter(UrlScans.schedule_id == self.schedule.id).all()
        for url in urls:
            extracted_cookies = self.session.query(ExtractedCookies).filter(ExtractedCookies.url_id == url.id).all()
            cookies = [self.session.query(Cookies).get(extracted_cookie.cookie_id) for extracted_cookie
                       in extracted_cookies]
            print enrich_cookie(cookies[0], self.session)
            for cookie in cookies:
                self.cookies.add_cookie(enrich_cookie(cookie, self.session))


def main():
    extractor = HtmlExtractor(8)
    extractor.generate_html()


if __name__ == '__main__':
    main()
