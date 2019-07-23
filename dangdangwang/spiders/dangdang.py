# -*- coding: utf-8 -*-
import re

import requests
import scrapy
from ..items import DangdangwangItem
from scrapy_redis.spiders import RedisCrawlSpider

class DangdangSpider(RedisCrawlSpider):
    name = 'dangdang'
    redis_key = 'dangdang:start_urls'
    allowed_domains = ['dangdang.com']
    # start_urls = ['http://search.dangdang.com/?key=python']

    def parse(self, response):
        url_list = response.xpath('//p[@class="name"]/a/@href').extract()
        for url in url_list:
            print(url)
            yield scrapy.Request(url=url,callback=self.parse_item)
        next_url = response.xpath('//li[@class="next"]/a/@href').extract_first()
        next_url = 'http://search.dangdang.com'+next_url
        print('详情页:' + next_url)
        if next_url != '':
            yield scrapy.Request(url=next_url,callback=self.parse)

    def parse_item(self, response):
        urls = str(response)
        m = re.search('http://product.dangdang.com/\d+.html', urls)
        # 使用正则匹配地址,判断是不是电子书
        # 不是电子书
        if m:
            item = DangdangwangItem()
            # 获取书名
            book_name = response.xpath('//div[@class="name_info"]/h1/@title').extract_first()
            item['book_name'] = book_name
            # 获取书的价钱
            book_price = response.xpath('//p[@id="dd-price"]/text()')[1].extract().strip()
            item['book_price'] = book_price
            # # 获取书的标题
            # book_introduction = response.xpath('//div[@id="product_info"]//h2/span/text()').extract_first().strip()
            # # book_introduction = ''.join(response.xpath('//div[@id="content"]/div[@class="descrip"]/text()').extract())
            # if book_introduction == '':
            #     item['book_introduction'] = '该书没有标明标题'
            # else:
            #     item['book_introduction'] = re.sub('\s', '', book_introduction)  # 将其中的所有空白字符删除
            # 获取到作者,出版社,出版时间的父标签
            spans = response.xpath('//div[@class="messbox_info"]/span')
            count = 0
            book_authors = ''  # 作者
            book_publishinghouse = ''  # 出版社
            book_publisheddate = ''  # 出版时间
            for span in spans:  # 遍历span标签,获取子节点,因为有三个子节点,分别包含作者、出版社以及出版时间
                if count == 0:  # 获取作者
                    ass = span.css('a')
                    for a in ass:  # 作者可能有多个,需要遍历
                        book_authors += a.css('::text').extract_first() + ','

                if count == 1:  # 获取出版社
                    ass = span.css('a')
                    if ass is None:
                        pass
                        book_publishinghouse = "没有标明出版社"
                    else:
                        book_publishinghouse = str(span.css('a::text').extract_first())

                if count == 2:  # 获取出版时间
                    book_publisheddate = str(span.css('::text').extract_first())

                count += 1
            item['book_authors'] = book_authors
            # 判断作者是否为空
            if item['book_authors'] == '':
                item['book_authors'] = '暂无作者信息'
            else:
                item['book_authors'] = book_authors[:-1]  # 使用切片删除字符串的最后一个字符,因为最后一个字符是逗号
            # item['book_publishinghouse'] = book_publishinghouse
            # 判断出版社是否为空
            book_publishinghouse = re.sub(' ', '', book_publishinghouse)  # 使用正则表达式爸空格字符转换成空字符,因为有的出版社信息是字符串
            item['book_publishinghouse'] = book_publishinghouse
            if item['book_publishinghouse'] == '':  # 判断出版社是否是空值
                item['book_publishinghouse'] = '没有标明出版社'
            elif item['book_publishinghouse'] == 'None':  # 判断出版社信息是否等于None,注意:这里的None是字符串.而不是关键字
                if item['book_authors'] == '':  # 如果出版社等于None就说明没有获取到数据,这里判断作者是否为空,因为有的书没有标明作者
                    item['book_publishinghouse'] = response.xpath(
                        '//div[@class="messbox_info"]/span/a/text').extract_first().strip()
                # item['book_publishinghouse'] = book_publishinghouse
                # item['book_publishinghouse'] = '没有标明出版社'

            if item['book_publishinghouse'] == '':
                item['book_publishinghouse'] = '没有标明出版社'
            else:
                item['book_publishinghouse'] = book_publishinghouse
            item['book_publisheddate'] = book_publisheddate
            # 判断出版时间是否为空
            book_publisheddate = re.sub(' ', '', book_publisheddate)
            item['book_publisheddate'] = book_publisheddate
            if item['book_publisheddate'] is None:
                item['book_publisheddate'] = '没有标明出版时间'
            elif item['book_authors'] != '' and item['book_publishinghouse'] == 'None' or item[
                'book_publishinghouse'] == '':
                # 判断作者是否不等于空,并且出版社等于空
                item['book_publisheddate'] = response.xpath('//div[@class="messbox_info"]/span/a/text')[1].extract().strip()
            elif item['book_authors'] == '' and item['book_publishinghouse'] == '' and item['book_publisheddate'] == '':
                item['book_authors'] = ''
                item['book_publishinghouse'] = ''
                item['book_publisheddate'] = ''
            elif item['book_authors'] == '' and item['book_publishinghouse'] == '':
                # 判断作者和出版社是否都为空
                # 测试
                item['book_publisheddate'] = response.xpath(
                    '//div[@class="messbox_info"]/span/a/text').extract_first().strip()
            elif item['book_authors'] == '':
                # 判断作者是否为空
                item['book_publisheddate'] = response.xpath('//div[@class="messbox_info"]/span/a/text')[
                    1].extract().strip()
            else:
                item['book_publisheddate'] = book_publisheddate
            # 获取评论数
            item['book_commentsnumbers'] = ''.join(response.xpath('//a[@id="comm_num_down"]/text()').extract())
            # 获取书的网址
            item['book_url'] = response.url
            if item['book_publisheddate'] == '':
                item['book_publisheddate'] = '没有标明出版时间'
            else:
                item['book_publisheddate'] = book_publisheddate
            item['book_commentsnumbers'] = ''.join(response.xpath('//a[@id="comm_num_down"]/text()').extract())
            # 获取书的网址
            item['book_url'] = response.url
            yield item
        else:
            # 电子书
            item = DangdangdemoWangItem()
            # 获取书名
            book_name = response.xpath('//div[@id="productBookDetail"]/h1/span/@title').extract_first()
            item['book_name'] = book_name
            # 获取书的价钱
            urls = response.url  # 获取json接口
            num = ''.join(re.findall('\d', urls))
            url = 'http://e.dangdang.com/media/api.go?action=getMedia&deviceSerialNo=html5&macAddr=' \
                  'html5&channelType=html5&permanentId=20190513102517003402311866144833876&returnType=j' \
                  'son&channelId=70000&clientVersionNo=6.8.0&platformSource=DDDS-P&fromPlatform=106&device' \
                  'Type=pconline&token=&refAction=browse&saleId=' + num + '&promotionType=1'
            print(url)

            price = requests.get(url)  # 想浏览器发送请求
            info = price.json()  # 解析json
            price1 = info['data']['mediaSale']
            price2 = dict(price1['mediaList'][0])  # 找到json中的数据
            price3 = price2['salePrice']  # 获取到价格
            book_price = price3  # 把价格赋值给book_price
            item['book_price'] = book_price

            # # 获取书的简介
            # book_introduction = price2['descs']
            # item['book_introduction'] = book_introduction
            # if book_introduction == '':
            #     item['book_introduction'] = '该书没有标明简介'
            # else:
            #     # item['book_introduction'] = re.sub('\s', '', book_introduction)  # 将其中的所有空白字符删除
            #     book_introduction = ''.join(book_introduction)
            #     item['book_introduction'] = re.sub('\s', '', book_introduction)

            # 获取到作者,出版社,出版时间的父标签
            spans = response.xpath('//div[@class="explain_box"]')
            count = 0
            book_authors = ''  # 作者
            for span in spans:  # 遍历span标签,获取子节点
                if count == 0:  # 获取作者
                    ass = span.css('p#author')
                    for a in ass:  # 作者可能有多个,需要遍历
                        book_authors += a.css('span a::text').extract_first() + ','
                count += 1
            # 判断作者是否为空
            if book_authors == '':
                item['book_authors'] = '没有标明作者'
            else:
                item['book_authors'] = book_authors[:-1]  # 使用切片删除字符串的最后一个字符,因为最后一个字符是逗号

            # 获取出版社
            book_publishinghouse = response.xpath('//p[@id="publisher"]/span/a/text()').extract_first()  # 出版社

            # 判断出版社是否为空
            if book_publishinghouse == '':
                item['book_publishinghouse'] = '该书没有标明出版社'
            elif book_publishinghouse is None:
                item['book_publishinghouse'] = '该书没有标明出版社'
            else:
                book_publishinghouse = response.xpath(
                    '//p[@id="publisher"]/span/a/text()').extract_first().strip()  # 出版社
                item['book_publishinghouse'] = book_publishinghouse

            # 判断出版社是否为空
            if item['book_publishinghouse'] == '':
                item['book_publishinghouse'] = '没有标明出版社'
            else:
                item['book_publishinghouse'] = book_publishinghouse

            # 获取出版时间
            book_publisheddate = response.xpath('//div[@class="explain_box"]/p/text()')[2].extract()  # 出版时间
            # 判断出版时间是否为空
            if book_publisheddate == '':
                item['book_publisheddate'] = '没有标明出版时间'
            # 判断出版时间是否为空
            elif book_publisheddate == '':
                item['book_publisheddate'] = '没有标明出版时间'
            else:
                nian = book_publisheddate[5:9]  # 获取出版时间中的年
                yue = book_publisheddate[10:12]  # 获取出版时间中的月
                # ri = book_publisheddate[13:15]  # 获取出版时间中的日
                book_publisheddate = '出版时间:' + nian + '年' + yue + '月'
                item['book_publisheddate'] = book_publisheddate

            # 获取评论数
            book_commentsnumber = response.xpath('//div[@class="count_per"]/em/text()')[0].extract()
            # item['book_commentsnumbers'] = book_commentsnumbers[0:1]
            book_commentsnumbers = re.sub('人评论', '', book_commentsnumber)  # 使用正则去空格
            item['book_commentsnumbers'] = book_commentsnumbers
            # 获取书的网址
            item['book_url'] = response.url
            yield item




