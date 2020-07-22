# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import re

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join


def re_match(value):
    re_mat = re.compile('.*?(\d+[.]\d+|\d+)')
    res = re.search(re_mat, value)
    if res:
        return res.group(1)

def return_value(value):
    return value


class BooksspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class BooksItem(scrapy.Item):
    name = scrapy.Field()
    in_stock = scrapy.Field(
        input_processor=MapCompose(re_match),
        output_processor=TakeFirst()
    )
    price = scrapy.Field(
        input_processor=MapCompose(re_match),
        output_processor=TakeFirst()
    )
    type = scrapy.Field()
    comment = scrapy.Field()
    url = scrapy.Field()
    front_cover_url = scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    front_cover_path = scrapy.Field()

class BooksItemLoader(ItemLoader):
    # 自定义itemloader
    default_output_processor = TakeFirst()

