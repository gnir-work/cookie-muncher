# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from sqlalchemy.orm import Session

from db import engine, UrlScans

SCHEDULE_ID = 'schedule_id'


class CookiemuncherPipeline(object):
    def __init__(self):
        self.session = Session(engine)

    def process_item(self, item, spider):
        self.session.add(UrlScans(schedule_id=spider.settings.get(SCHEDULE_ID), url=item['link']))
        self.session.commit()
        return item

    def close_spider(self, spider):
        print('Closed session with mysql from pipeline')
        self.session.close()
