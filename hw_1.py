"""
Задача организовать сбор данных,
необходимо иметь метод сохранения данных в .json файлы
результат: Данные скачиваются с источника, при вызове метода/функции сохранения в файл скачанные данные сохраняются в Json вайлы, для каждой категории товаров должен быть создан отдельный файл и содержать товары исключительно соответсвующие данной категории.
пример структуры данных для файла:
нейминг ключей можно делать отличным от примера

{
"name": "имя категории",
"code": "Код соответсвующий категории (используется в запросах)",
"products": [{PRODUCT}, {PRODUCT}........] # список словарей товаров соответсвующих данной категории
}
"""
import requests
import json
from pathlib import Path
import time


class Parse5ka:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
    }
    params = {"records_per_page": 20}

    def __init__(self, start_url: str, save_path: Path):
        self.start_url = start_url
        self.save_path = save_path

    def _get_response(self, url, *args, **kwargs):
        url = url.replace('monolith', '5ka.ru')
        while True:
            response = requests.get(url, *args, **kwargs)
            if response.status_code == 200:
                return response
            time.sleep(1)

    def _parse(self, url: str):
        while url:
            time.sleep(0.1)
            response = self._get_response(url, headers=self.headers, params = self.params)
            data = response.json()
            url = data['next']
            for product in data['results']:
                yield product

    def run(self):
        for product in self._parse(self.start_url):
            file_path = self.save_path.joinpath(f'{product["id"]}.json')
            self._save(product, file_path)

    def _save(self, data: dict, file_path):
        file_path.write_text(json.dumps(data, ensure_ascii=False))


class ParseCategory(Parse5ka):
    url_cat = 'https://5ka.ru/api/v2/categories/'

    def _get_categories(self):
        response = self._get_response(self.url_cat)
        self.categories = response.json()

    def run(self):
        self._get_categories()
        for category in self.categories:
            self.params['categories'] = int(category['parent_group_code'])
            products = []
            for product in self._parse(self.start_url):
                products.append(product)
            data = {'name': category['parent_group_name'], 'code': category['parent_group_code'], 'products': products}
            file_path = self.save_path.joinpath(f'{category["parent_group_name"]}.json')
            self._save(data, file_path)


def get_save_path(dir_name):
    save_path = Path(__file__).parent.joinpath(dir_name)
    if not save_path.exists():
        save_path.mkdir()
    return save_path

if __name__ == '__main__':
    url = "http://5ka.ru/api/v2/special_offers/"
    save_path = get_save_path('products')
    cat_parser = ParseCategory(url, save_path)
    cat_parser.run()
