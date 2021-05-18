# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TagParseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    date_parse = scrapy.Field()
    data = scrapy.Field()


class PostParseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    date_parse = scrapy.Field()
    data = scrapy.Field()