# -*- coding: utf-8 -*-
import re
import scrapy

from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from ChinaBuildingMaterialsNetwork.items import ProductItem, ImageItem, CompanyItem, CompanyIdItem


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

        product['basic_information'] = {}
        product_name = response.xpath('//div[@class="sellinfo"]/h1/text()').extract_first()
        if product_name:
            product['basic_information']['product_name'] = product_name
            product['product_name'] = product_name

        product['basic_information']['prices_quantity'] = []
        dd_list = response.xpath('//div[@class="sellinfo"]/dl/dd')
        for dd in dd_list:
            dd_dict = {}
            price = dd.xpath('./p[@class="price"]/text()').extract_first()
            if price:
                dd_dict['price'] = price
            else:
                price = dd.xpath('./p[@class="price dy"]/text()').extract_first()
                if price:
                    dd_dict['price'] = price
            minimum_quantity = dd.xpath('./p[@class="order"]/text()').extract_first()
            if minimum_quantity:
                dd_dict['minimum_quantity'] = minimum_quantity
            if dd_dict:
                product['basic_information']['prices_quantity'].append(dd_dict)

        minimum_order_quantity = response.xpath('//div[@class="sellinfo"]/ul/li[1]/text()').extract_first()
        if minimum_order_quantity:
            product['basic_information']['minimum_order_quantity'] = minimum_order_quantity
        location = response.xpath('//div[@class="sellinfo"]/ul/li[2]/text()').extract_first()
        if location:
            product['basic_information']['location'] = location
        total_supply = response.xpath('//div[@class="sellinfo"]/ul/li[4]/text()').extract_first()
        if total_supply:
            product['basic_information']['total_supply'] = total_supply
        delivery_date = response.xpath('//div[@class="sellinfo"]/ul/li[5]/text()').extract_first()
        if delivery_date:
            product['basic_information']['delivery_date'] = delivery_date
        release_time = response.xpath('//div[@class="sellinfo"]/ul/li[6]/text()').extract_first()
        if release_time:
            product['basic_information']['release_time'] = release_time
        contact = response.xpath('//div[@class="sellinfo"]/p/b/text()').extract_first()
        if contact:
            product['basic_information']['contact'] = contact

        product['basic_information']['big_photos'] = []
        big_photos_list = response.xpath('//div[@class="m-productTab"]/div[@class="m-bd"]/ul//img/@src').extract()
        if big_photos_list:
            item = ImageItem()
            item['image_urls'] = []
            for photo in big_photos_list:
                original_url = photo
                local_url = 'E:/images' + photo.split('com')[-1]
                image_detailed_url = {'original_url': original_url,
                                      'local_url': local_url}
                product['basic_information']['big_photos'].append(image_detailed_url)
                item['image_urls'].append(original_url)
            yield item

        product['basic_information']['small_photos'] = []
        small_photos_list = response.xpath('//div[@class="m-productTab"]/ul[@class="m-hd"]//img/@src').extract()
        if small_photos_list:
            item = ImageItem()
            item['image_urls'] = []
            for photo in small_photos_list:
                original_url = photo
                local_url = 'E:/images' + photo.split('com')[-1]
                image_detailed_url = {'original_url': original_url,
                                      'local_url': local_url}
                product['basic_information']['small_photos'].append(image_detailed_url)
                item['image_urls'].append(original_url)
            yield item

        product['detail_information'] = {}
        is_product_parameters = response.xpath('//div[@class="m-productInfo"]/ul')
        if is_product_parameters:
            product['detail_information']['product_parameters'] = {}
            parameters_number = len(response.xpath('//div[@class="m-productInfo"]/ul/li').extract())
            if parameters_number != 0:
                for parameter in range(1, parameters_number + 1):
                    type_xpath = '//div[@class="m-productInfo"]/ul/li[{number}]/p[@class="type"]/text()'
                    parameter_key = response.xpath(type_xpath.format(number=parameter)).extract_first()
                    info_xpath = '//div[@class="m-productInfo"]/ul/li[{number}]/p[@class="info"]/text()'
                    parameter_value = response.xpath(info_xpath.format(number=parameter)).extract_first()
                    if parameter_key and parameter_value:
                        product['detail_information']['product_parameters'][parameter_key] = parameter_value

        is_detailed_description = response.xpath('//div[@class="m-productInfo"]/div[@class="detail"]')
        if is_detailed_description:
            product['detail_information']['detailed_description'] = []
            p_numbers = len(response.xpath('//div[@class="m-productInfo"]/div[@class="detail"]/p').extract())
            if p_numbers:
                for p in range(1, p_numbers + 1):
                    p_text_xpath = 'string(//div[@class="m-productInfo"]/div[@class="detail"]/p[{number}])'
                    p_text = response.xpath(p_text_xpath.format(number=p)).extract_first().strip()
                    if p_text:
                        product['detail_information']['detailed_description'].append(p_text)
                    p_image_xpath = '//div[@class="m-productInfo"]/div[@class="detail"]/p[{number}]/img/@src'
                    image_list = response.xpath(p_image_xpath.format(number=p)).extract()
                    if image_list:
                        item = ImageItem()
                        item['image_urls'] = []
                        image_number = len(image_list)
                        for image in range(0, image_number):
                            image_original_url = image_list[image]
                            image_local_url = 'E:/images' + image_original_url.split('com')[-1]
                            image_detailed_url = {'image_original_url': image_original_url,
                                                  'image_local_url': image_local_url}
                            product['detail_information']['detailed_description'].append(image_detailed_url)
                            item['image_urls'].append(image_original_url)
                        yield item

        is_trading_certificate = response.xpath('//div[@class="m-certificate"]')
        if is_trading_certificate:
            product['detail_information']['trading_certificate'] = []
            certificate_photo_list = response.xpath('//div[@class="m-certificate"]//img/@src').extract()
            if certificate_photo_list:
                item = ImageItem()
                item['image_urls'] = []
                for photo in certificate_photo_list:
                    certificate_original = photo
                    certificate_local = 'E:/images' + photo.split('com')[-1]
                    image_detailed_url = {'image_original_url': certificate_original,
                                          'image_local_url': certificate_local}
                    product['detail_information']['trading_certificate'].append(image_detailed_url)
                    item['image_urls'].append(certificate_original)
                yield item

        product['company'] = {}
        product['company']['$ref'] = 'company'
        product['company']['$id'] = response.xpath('//div[@class="head-product"]/h2/text()').extract_first()

        product_item = ProductItem()
        for field in product_item.fields:
            if field in product.keys():
                product_item[field] = product.get(field)
        yield product_item

        le = LinkExtractor(restrict_xpaths='//li[@id="nav-company"]/a')
        links = le.extract_links(response)
        if links:
            for link in links:
                yield Request(link.url, callback=self.parse_company)

    def parse_company(self, response):
        item = CompanyIdItem()
        item['_id'] = response.xpath('//div[@class="head-product"]/h2/text()').extract_first()
        yield item

        company = {'_id': response.xpath('//div[@class="head-product"]/h2/text()').extract_first(),
                   'company_profile': {}}
        is_photos = response.xpath('//div[@class="m-tab4"]/div[@class="m-bd"]/ul')
        if is_photos:
            company['company_profile']['big_photos'] = []
            company['company_profile']['small_photos'] = []
            big_photos_list = response.xpath('//div[@class="m-tab4"]/div[@class="m-bd"]/ul//img/@src').extract()
            if big_photos_list:
                item = ImageItem()
                item['image_urls'] = []
                for photo in big_photos_list:
                    original_url = photo
                    local_url = 'E:/images' + photo.split('com')[-1]
                    image_detailed_url = {'original_url': original_url,
                                          'local_url': local_url}
                    company['company_profile']['big_photos'].append(image_detailed_url)
                    item['image_urls'].append(original_url)
            small_photos_list = response.xpath('//div[@class="m-tab4"]/ul[@class="m-hd"]/li//img/@src').extract()
            if small_photos_list:
                item = ImageItem()
                item['image_urls'] = []
                for photo in small_photos_list:
                    original_url = photo
                    local_url = 'E:/images' + photo.split('com')[-1]
                    image_detailed_url = {'original_url': original_url,
                                          'local_url': local_url}
                    company['company_profile']['small_photos'].append(image_detailed_url)
                    item['image_urls'].append(original_url)
        company['company_profile']['introduction'] = []
        p_list = response.xpath('//div[@class="detail"]/p//text()').extract()
        if p_list:
            for p in p_list:
                if p.strip():
                    company['company_profile']['introduction'].append(p)
        else:
            p = response.xpath('//div[@class="detail"]//text()').extract_first().strip()
            if p:
                company['company_profile']['introduction'].append(p)
        company['company_profile']['basic_information'] = {}
        li_list = response.xpath('//div[@class="m-companyInfo"]/div[4]//li')
        if li_list:
            for li in li_list:
                p_key = li.xpath('./p[@class="type"]//text()').extract_first()
                p_value = li.xpath('./p[@class="info"]//text()').extract_first()
                if p_key and p_value:
                    company['company_profile']['basic_information'][p_key] = p_value
        company['company_profile']['detail_information'] = {}
        li_list = response.xpath('//div[@class="m-companyInfo"]/div[5]//li')
        if li_list:
            for li in li_list:
                p_key = li.xpath('./p[@class="type"]//text()').extract_first()
                p_value = li.xpath('./p[@class="info"]//text()').extract_first()
                if p_key and p_value:
                    company['company_profile']['detail_information'][p_key] = p_value

        item = CompanyItem()
        for field in item.fields:
            if field in company.keys():
                item[field] = company.get(field)
        yield item

        le = LinkExtractor(restrict_xpaths='//li[@id="nav-contact"]/a')
        links = le.extract_links(response)
        if links:
            for link in links:
                yield Request(link.url, callback=self.parse_contact)

    def parse_contact(self, response):
        card = response.xpath('//div[@class="card"]')
        if card:
            company = {'_id': response.xpath('//div[@class="head-product"]/h2/text()').extract_first(),
                       'contact': {}}
            link_man = card.xpath('./div[@class="cardName"]/h3/text()').extract_first()
            if link_man:
                company['contact']['link_man'] = link_man
            position = card.xpath('./div[@class="cardName"]/h3/em/text()').extract_first()
            if position:
                company['contact']['position'] = position
            dd_dt_list = card.xpath('./dl[@class="cardInfo"]/*/text()').extract()
            if dd_dt_list:
                for dd in dd_dt_list:
                    dd = dd.split('：')
                    if len(dd) == 2:
                        key = dd[0]
                        value = dd[1]
                        company['contact'][key] = value

            item = CompanyItem()
            for field in item.fields:
                if field in company.keys():
                    item[field] = company.get(field)
            yield item
