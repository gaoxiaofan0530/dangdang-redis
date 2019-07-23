# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DangdangwangItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 书名
    book_name = scrapy.Field()
    # 书的售价
    book_price = scrapy.Field()
    # # 书的简介
    # book_introduction = scrapy.Field()
    # 书的作者
    book_authors = scrapy.Field()
    # 出版社
    book_publishinghouse = scrapy.Field()
    # 出版时间
    book_publisheddate = scrapy.Field()
    # 评论数
    book_commentsnumbers = scrapy.Field()
    # 网址
    book_url = scrapy.Field()
