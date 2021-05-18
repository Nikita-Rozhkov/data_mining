from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst


class TagLoader(ItemLoader):
    default_item_class = dict
    date_parse_out = TakeFirst()
    data_out = TakeFirst()


class PostLoader(ItemLoader):
    default_item_class = dict
    date_parse_out = TakeFirst()
    data_out = TakeFirst()