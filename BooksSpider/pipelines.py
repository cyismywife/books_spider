# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json

import pymysql
import pymysql.cursors

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from BooksSpider.utils.with_mysql import MySQLContextManager

from twisted.enterprise import adbapi

class BooksspiderPipeline:
    def process_item(self, item, spider):
        return item


class JsonWithEncodingPipeline:
    def __init__(self):
        self.file = codecs.open('book.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + '\n'
        self.file.write(lines)
        return item

    def close_spider(self, spider):
        self.file.close()


class JsonItemExporterPipeline:
    # 调用scrapy提供的json export导出json文件
    def __init__(self):
        self.file = open('books.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class MysqlExportPipeline:
    # 自己定义的数据库插入类,, 同步机制
    def __init__(self):
        self.DB = MySQLContextManager(host='47.96.183.136', port=3306, user="root", password="Admin123!", database="spider")

    def process_item(self, item, spider):
        with self.DB as DB:
            values = tuple((value if not isinstance(value, list) else value[0] for _, value in item.items()))
            insert_sql = 'INSERT INTO books_spider (url, name, price, in_stock, type, comment, front_cover_url, front_cover_path) VALUES {values}'.format(values=values)
            DB.execute(insert_sql)
        return item


class MysqkTwistedPipeline:
    # 异步
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            password=settings['MYSQL_PASSWORD'],
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('pymysql', **dbparms)

        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted 使mysql插入异步化
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)  # 处理异常

    def handle_error(self, failure, item, spider):
        #处理异步出现的错误
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        values = tuple((value if not isinstance(value, list) else value[0] for _, value in item.items()))
        insert_sql = 'INSERT INTO books_spider (url, name, price, in_stock, type, comment, front_cover_url, front_cover_path) VALUES {values}'.format(
            values=values)
        cursor.execute(insert_sql)


class BookImagesPipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if 'front_cover_url' in item:
            for ok, value in results:
                book_image_path = value['path']
            item['front_cover_path'] = book_image_path

        return item



