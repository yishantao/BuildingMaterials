# -*- coding: utf-8 -*-
import re
import scrapy

from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from ChinaBuildingMaterialsNetwork.items import ProductItem


class MaterialSpider(scrapy.Spider):
    name = 'material'
    allowed_domains = ['www.bmlink.com']
    start_urls = ['https://www.bmlink.com/supply/list.html']

    def start_requests(self):
        for url in self.start_urls:
            yield self.make_requests_from_url(url)

    def make_requests_from_url(self, url):
        return Request(url, dont_filter=True)

    def parse(self, response):
        le = LinkExtractor(restrict_xpaths='//div[@class="sContentD"]/div[1]//a[position()>1 and position()<3]')
        links = le.extract_links(response)
        if links:
            for link in links:
                yield Request(link.url, callback=self.parse_category_one)

    def parse_category_one(self, response):
        is_category = response.xpath('//div[@class="sContentD"]/div[1]/h3[contains(text(),"类目")]').extract()
        if is_category:
            le = LinkExtractor(restrict_xpaths='//div[@class="sContentD"]/div[1]//a[position()>1]')
            links = le.extract_links(response)
            if links:
                for link in links:
                    yield Request(link.url, callback=self.parse_category_two)
        else:
            yield Request(response.url, callback=self.parse_category_three)

    def parse_category_two(self, response):
        is_category = response.xpath('//div[@class="sContentD"]/div[1]/h3[contains(text(),"类目")]').extract()
        if is_category:
            le = LinkExtractor(restrict_xpaths='//div[@class="sContentD"]/div[1]//a[position()>1 and position()<3]')
            links = le.extract_links(response)
            if links:
                for link in links:
                    yield Request(link.url, callback=self.parse_category_three)
        else:
            yield Request(response.url, callback=self.parse_category_three)

    def parse_category_three(self, response):
        pattern = 'supply/.*'
        category = re.search(pattern=pattern, string=response.url).group()[7:]
        pattern = '\d/\d*'
        string = response.xpath('//span[@class="paginationInfo"]/text()').extract_first()
        if string:
            total_page = re.search(pattern=pattern, string=string).group()[2:]
            for page in range(1, int(total_page) + 1):
                page_url = 'https://www.bmlink.com/supply/list-p{page}-py{category}.html'
                page_url = page_url.format(page=page, category=category)
                yield Request(page_url, callback=self.parse_category_last)
        else:
            pass

    def parse_category_last(self, response):
        le = LinkExtractor(restrict_xpaths='//ul[@class="m-ilist3 clearfix"]/li/a[1]')
        links = le.extract_links(response)
        if links:
            for link in links:
                yield Request(link.url, callback=self.parse_product)

    def parse_product(self, response):
        # 起订量 = response.xpath('//div[@class="sellinfo"]/dl/dd/p[@class="order"]/text()').extract_first()
        # 价格 = response.xpath('//div[@class="sellinfo"]/dl/dd/p[@class="price"]/text()').extract_first()
        # 最小起订量 = response.xpath('//div[@class="sellinfo"]/ul/li[1]/text()').extract_first()
        product = {}
        category_one = response.xpath('//div[@id="location"]/a[3]/text()').extract_first()
        if category_one:
            product['category_one'] = category_one
        category_two = response.xpath('//div[@id="location"]/a[4]/text()').extract_first()
        if category_two:
            product['category_two'] = category_two
        category_three = response.xpath('//div[@id="location"]/a[5]/text()').extract_first()
        if category_three:
            product['category_three'] = category_three
        item = ProductItem()
        for field in item.fields:
            if field in product.keys():
                item[field] = product.get(field)
        

        # item['product_name'] = response.xpath('//div[@class="sellinfo"]/h1/text()').extract_first()

