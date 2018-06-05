# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class ChinabuildingmaterialsnetworkItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ProductItem(Item):
    product_name = Field()
    company = Field()
    category_one = Field()
    category_two = Field()
    category_three = Field()
    basic_information = Field()
    detail_information = Field()


class CompanyItem(Item):
    _id = Field()
    company_name = Field()
    company_profile = Field()
    recruitment = Field()
    contact = Field()


class CompanyIdItem(Item):
    _id = Field()
    # company_name = Field()


class ImageItem(Item):
    image_urls = Field()
    images = Field()
    image_paths = Field()
