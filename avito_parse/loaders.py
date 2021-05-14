from urllib.parse import urljoin

from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose


def flat_text(items):
    return "\n".join(items)


class AvitoLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_out = TakeFirst()
    price_out = TakeFirst()
    address_out = flat_text
    description_in = flat_text
    description_out = flat_text
    author_in = MapCompose(lambda user_id: urljoin("https://www.avito.ru/", user_id))
    author_out = TakeFirst()