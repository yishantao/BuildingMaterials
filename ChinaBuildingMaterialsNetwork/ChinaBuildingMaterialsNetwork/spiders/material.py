# -*- coding: utf-8 -*-
import scrapy

from scrapy import Request


class MaterialSpider(scrapy.Spider):
    name = 'material'
    allowed_domains = ['www.bmlink.com']
    start_urls = ['http://www.bmlink.com/']

    def start_requests(self):
        for url in self.start_urls:
            yield self.make_requests_from_url(url)

    def make_requests_from_url(self, url):
        return Request(url, dont_filter=True)

    def parse(self, response):
        print(response.body)


from scrapy.selector import Selector
from scrapy.http import HtmlResponse

body = 'HTML文档'
response = HtmlResponse(url='', body=body, encoding='utf8')
selector = Selector(response=response)
