import scrapy

from avito_parse.loaders import AvitoLoader

avito_page_xpath = {
    "pagination": '//div[contains(@class, "pagination-hidden")]//a[@class="pagination-page"]/@href',
    "offer": '//div[contains(@class, "iva-item-root")]//div[contains(@class, "iva-item-titleStep")]//'
    'a[contains(@class, "title-root")]/@href',
}

avito_offer_xpath = {
    "title": '//span[@class="title-info-title-text"]/text()',
    "price": '//div[@id="price-value"]//span[@class="js-item-price"]/@content',
    "address": '//span[@class="item-address__string"]/text()',
    "description": '//div[@class="item-params-title" and contains(text(), "О квартире")]'
                   '/following-sibling::ul/li/text()',
    "author": '//div[@data-marker="seller-info/name"]/a/@href',
}

class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru']
    start_urls = ['https://www.avito.ru/domodedovo/kvartiry/prodam/']
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-GB,en;q=0.5",
        "Connection": "keep-alive",
    }

    def _get_follow_xpath(self, response, xpath, callback):
        for url in response.xpath(xpath):
            yield response.follow(url, callback=callback, headers=self.headers)

    def parse(self, response):
        callbacks = {"pagination": self.parse, "offer": self.offer_parse}

        for key, xpath in avito_page_xpath.items():
            yield from self._get_follow_xpath(response, xpath, callbacks[key])

    def offer_parse(self, response):
        loader = AvitoLoader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in avito_offer_xpath.items():
            loader.add_xpath(key, xpath)
        yield loader.load_item()