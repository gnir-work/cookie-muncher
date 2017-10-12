from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.crawler import CrawlerProcess
from datetime import datetime as dt
import random
from cookieMuncher.items import CookieMuncherItem

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1',
    'Mozilla/5.0 (X11; Linux x86_64; rv:17.0) Gecko/20121202 Firefox/17.0 Iceweasel/17.0.1',
    'Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
]


class CookieMuncherSpider(CrawlSpider):
    name = "cookieMuncher"
    rules = (
        Rule(LinkExtractor(allow=()),
             callback="parse_item",
             follow=True),)

    def __init__(self, start_urls, allowed_domains, *args, **kwargs):
        super(CookieMuncherSpider, self).__init__(*args, **kwargs)
        self.allowed_domains = allowed_domains
        self.start_urls = start_urls

    def parse_item(self, response):
        item = CookieMuncherItem()
        item['link'] = response.url
        item['time'] = dt.now()
        return item


def crawl(urls, allowed_domains, depth, silent, log_file, output_file, delay, user_agent):
    """
    Start crawling with CookieMuncher spider.
    :param urls: The list of urls from which the crawlers should start crawling
    :param allowed_domains: The list of allowed domains, if empty list is passed all of the domains are allowed.
    :param depth: The depth the crawler should crawl to.
    :param silent: If True the crawler wont write any logs
    :param log_file: The path to the log file.
    :param output_file: The path to the output of the crawler.
    """
    process = CrawlerProcess({
        'USER_AGENT': user_agent if user_agent else random.choice(USER_AGENTS),
        'DEPTH_LIMIT': depth,
        'FEED_URI': output_file,
        'FEED_FORMAT': 'csv',
        'LOG_ENABLED': not silent,
        'LOG_FILE': log_file,
        'DOWNLOAD_DELAY': delay,
        'COOKIES_ENABLED': False
    })
    process.crawl(CookieMuncherSpider, urls, allowed_domains)
    process.start()  # the script will block here until the crawling is finished
