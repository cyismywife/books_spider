# -*- coding: utf-8 -*-
import re
from urllib.parse import urljoin

import scrapy
from scrapy.loader import ItemLoader

from BooksSpider.items import BooksItem, BooksItemLoader
from BooksSpider.utils.common import get_md5

class BooksSpider(scrapy.Spider):
    name = 'books'
    allowed_domains = ['books.toscrape.com']
    # start_urls = ['http://books.toscrape.com/']
    # start_urls = ['http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html']
    start_urls = ['http://books.toscrape.com/catalogue/category/books_1/page-1.html']
    url_base = 'http://books.toscrape.com/catalogue/'
    url_next_base = 'http://books.toscrape.com/catalogue/category/books_1/'

    def parse(self, response):
        """
        1, 获取图书列表中的每本书的url并交给解析函数进行字段的解析。
        2， 获取下一页的url并交给scrapy进行下载。
        :param response:
        :return:
        """
        #1.0 解析列表页中的每本书的url
        # urls = response.css('div.image_container a::attr(href)')
        # urlss = [urljoin(self.url_base, url.split('/', 2)[-1]) for url in urls]
        # for url in urlss:
        #     yield scrapy.Request(url=url, callback=self.detail_parse)

        #2.0 解析列表页中的每本书的url
        urls = response.css('div.image_container a')
        for url in urls:
            image_url = url.css('a img::attr(src)').extract_first()
            book_url = url.css('a::attr(href)').extract_first()
            yield scrapy.Request(url=urljoin(self.url_base, book_url.split('/', 2)[-1]), meta={
                'front_cover': urljoin(response.url, image_url)},
                                 callback=self.detail_parse)

        # 获取下一个列表页，并解析其中每本书的url
        next = response.css('li.next a::attr(href)').extract_first()
        if next:
            # yield scrapy.Request(url=urljoin(self.url_next_base, next), callback=self.parse)
            yield scrapy.Request(url=urljoin(response.url, next), callback=self.parse)

    def detail_parse(self, response):
        """解析每本书具体的信息, 它也是个回调函数"""
        # booksitem = BooksItem()
        # re_mat = re.compile('.*?(\d+[.]\d+|\d+)')
        #
        # # 通过xpath提取元素
        # url = response.url
        # name = response.xpath('//*[@id="content_inner"]/article/div[1]/div[2]/h1/text()').extract_first('')  # 书名
        # price = response.xpath('//*[@id="content_inner"]/article/div[1]/div[2]/p[1]/text()').extract_first('')  # 价格
        # price = float(re.search(re_mat, price).group(1))
        # in_stock = response.xpath('//*[@id="content_inner"]/article/table/tr[6]/td/text()').extract_first('')
        # in_stock = int(re.search(re_mat, in_stock).group(1))
        # type = response.xpath('//*[@id="default"]/div/div/ul/li[3]/a/text()').extract_first('')  # 类别
        # comment = int(response.xpath('//*[@id="content_inner"]/article/table/tr[7]/td/text()').extract_first(''))  # 评论数
        front_cover_url = response.meta.get('front_cover', '')  # 图书封面url
        #
        # # front_cover = response.xpath('//*[@id="product_gallery"]/div/div/div/img/@src').extract_first('')  # 图书封面url
        #
        # booksitem['url'] = response.url
        # booksitem['name'] = name
        # booksitem['price'] = price
        # booksitem['in_stock'] = in_stock
        # booksitem['type'] = type
        # booksitem['comment'] = comment
        # booksitem['front_cover_url'] = [front_cover_url]

        # 通过css选择
        # name = response.css('div.col-sm-6.product_main h1::text').extract_first()  # 书名
        # price = response.css('p.price_color::text').extract_first()  # 价格
        # comment = response.css('table.table.table-striped>tr:nth-child(7) td::text').extract_first()  # 评论数

        # 通过ItemLoader加载item
        item_loader = BooksItemLoader(item=BooksItem(), response=response)
        item_loader.add_value('url', get_md5(response.url))
        item_loader.add_css('name', 'div.col-sm-6.product_main h1::text')
        item_loader.add_xpath('price', '//*[@id="content_inner"]/article/div[1]/div[2]/p[1]/text()')
        item_loader.add_xpath('in_stock', '//*[@id="content_inner"]/article/table/tr[6]/td/text()')
        item_loader.add_xpath('type', '//*[@id="default"]/div/div/ul/li[3]/a/text()')
        item_loader.add_xpath('comment', '//*[@id="content_inner"]/article/table/tr[7]/td/text()')
        item_loader.add_value('front_cover_url', [front_cover_url])



        booksitem = item_loader.load_item()

        yield booksitem

