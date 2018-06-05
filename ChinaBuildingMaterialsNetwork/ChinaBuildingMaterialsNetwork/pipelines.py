# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo

from scrapy import Request
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
from ChinaBuildingMaterialsNetwork.items import ProductItem, ImageItem, CompanyItem


class ChinabuildingmaterialsnetworkPipeline(object):
    def process_item(self, item, spider):
        return item


class MongoPipeline(object):
    collection_name_product = 'product'
    collection_name_company = 'company'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        # True表示如果没有更新就插入
        if isinstance(item, ProductItem):
            if 'product_name' in item.keys():
                self.db[self.collection_name_product].update({'product_name': item['product_name']},
                                                             {'$set': dict(item)}, True)
                return item
        elif isinstance(item, CompanyItem):
            if 'company_name' in item.keys():
                self.db[self.collection_name_company].update({'company_name': item['company_name']},
                                                             {'$set': dict(item)}, True)
                return item
        return item


class ImagePipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None):
        url = request.url
        file_name = url.split('com')[-1]
        return file_name

    def item_completed(self, results, item, info):
        if isinstance(item, ImageItem):
            image_paths = [x['path'] for ok, x in results if ok]
            if not image_paths:
                raise DropItem('Image Downloaded Failed')
            item['image_paths'] = image_paths
            return item
        return item

    def get_media_requests(self, item, info):
        if isinstance(item, ImageItem):
            for image_url in item['image_urls']:
                yield Request(image_url)
