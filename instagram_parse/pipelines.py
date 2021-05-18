# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from .settings import BOT_NAME
from pymongo import MongoClient


class InstagramParsePipeline:
    def __init__(self):
        client = MongoClient()
        self.db = client[BOT_NAME]

    def process_item(self, item, spider):
        self.db[spider.name + type(item).__name__].insert_one(ItemAdapter(item).asdict())
        return item


class InstagramImageDownloadPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['data'].get("carousel_media"):
            for media in item['data'].get("carousel_media"):
                yield Request(media["image_versions2"]["candidates"][0]['url'])
        else:
            if item['data'].get("image_versions2"):
                yield Request(item['data']["image_versions2"]["candidates"][0]['url'])

    def item_completed(self, results, item, info):
        if item['data'].get("carousel_media"):
            for media in item['data'].get("carousel_media"):
                media["image_versions2"]["candidates"] = [itm[1] for itm in results]
        else:
            if item['data'].get("image_versions2"):
                item['data']["image_versions2"]["candidates"] = [itm[1] for itm in results]
        return item