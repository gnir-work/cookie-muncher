from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.crawler import CrawlerProcess
from urlparse import urlparse
from datetime import datetime as dt

from cookieMuncher.items import CookieMuncherItem


class CookieMuncherSpider(CrawlSpider):
    name = "test"
    rules = (
        Rule(LinkExtractor(allow=()),
             callback="parse_item",
             follow=True),)

    def __init__(self, start_urls, allowed_domains, *args, **kwargs):
        super(CookieMuncherSpider, self).__init__(*args, **kwargs)
        self.allowed_domains = allowed_domains
        self.start_urls = start_urls
        print self.allowed_domains
        print self.start_urls

    def parse_item(self, response):
        item = CookieMuncherItem()
        item['link'] = response.url
        item['time'] = dt.now()
        return item

def crawl(url, domain_only, depth, silent, log_file, output_file):
    """
    Start crawling with CookieMuncher spider.
    :param url: The url from which the crawlers should start crawling
    :param domain_only: If True the crawlers will only crawl links from the given domain
    :param depth: The depth the crawler should crawl to.
    :param silent: If True the crawler wont write any logs
    :param log_file: The path to the log file.
    :param output_file: The path to the output of the crawler.
    """
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'DEPTH_LIMIT': depth,
        'FEED_URI': output_file,
        'FEED_FORMAT': 'csv',
        'LOG_ENABLED': not silent,
        'LOG_FILE': log_file,
    })
    process.crawl(CookieMuncherSpider, [url], [urlparse(url).netloc] if domain_only else [])
    process.start()  # the script will block here until the crawling is finished
