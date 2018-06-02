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
    category_one = Field()
    category_two = Field()
    category_third = Field()
    product_base_info = Field()
    product_detail_info = Field()
