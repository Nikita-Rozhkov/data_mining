import json
import html2text
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Compose, Join


def get_description(data):
    description = html2text(json.loads(data)["description"])
    return description


def get_author(data):
    author_url = "https://hh.ru" + data
    return author_url


def get_title(data):
    title = "".join(item for item in data if item != " ")
    return title


def get_activity(data):
    activity = "".join(data).split(sep=', ')
    return activity


class VacancyLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_in = Join("")
    title_out = TakeFirst()
    price_in = Join("")
    price_out = TakeFirst()
    description_in = MapCompose(get_description)
    description_out = TakeFirst()
    author_in = MapCompose(get_author)
    author_out = TakeFirst()


class AuthorLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_in = Compose(get_title)
    title_out = TakeFirst()
    website_out = TakeFirst()
    activity_out = MapCompose(get_activity)
    description_in = Join("")
    description_out = TakeFirst()