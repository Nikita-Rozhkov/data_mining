import scrapy
from ..loaders import VacancyLoader, AuthorLoader

xpath_selectors = {
    "pages": '//a[@data-qa="pager-next"]/@href',
    "vacancy": '//a[@data-qa="vacancy-serp__vacancy-title"]/@href',
    "author": '//a[@data-qa="vacancy-company-name"]/@href'
}
xpath_vacancy_data_selectors = {
    "title": "//h1//text()",
    "price": "//p[@class='vacancy-salary']/span/text()",
    "description": "//script[@type='application/ld+json']/text()",
    "tags": "//span[@data-qa='bloko-tag__text']/text()",
    "author": '//a[@data-qa="vacancy-company-name"]/@href'
}
xpath_author_data_selectors = {
    "title": "//div[@class='company-header']//h1//text()",
    "website": "//a[@data-qa='sidebar-company-site']/@href",
    "activity": "//div[@class='employer-sidebar-block']/p/text()",
    "description": "//div[@data-qa='company-description-text']//text()",
    "vacancies": "//a[@data-qa='vacancy-serp__vacancy-title']/@href",
}

class HhSpider(scrapy.Spider):
    name = "hh"
    allowed_domains = ["hh.ru"]
    start_urls = ["https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113"]

    def _get_follow(self, response, selector_str, callback):
        for item in response.xpath(selector_str):
            yield response.follow(item, callback=callback)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(
            response, xpath_selectors["pages"], self.parse
        )
        yield from self._get_follow(
            response, xpath_selectors["vacancy"], self.vacancy_parse,
        )

    def vacancy_parse(self, response):
        loader = VacancyLoader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in xpath_vacancy_data_selectors.items():
            loader.add_xpath(key, xpath)
        yield loader.load_item()
        yield from self._get_follow(
            response, xpath_selectors["author"], self.author_parse,
        )

    def author_parse(self, response):
        loader = AuthorLoader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in xpath_author_data_selectors.items():
            loader.add_xpath(key, xpath)
        yield loader.load_item()
