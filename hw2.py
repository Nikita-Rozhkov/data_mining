"""
Источник https://gb.ru/posts/
Необходимо обойти все записи в блоге и извлеч из них информацию следующих полей:
url страницы материала
Заголовок материала
Первое изображение материала (Ссылка)
Дата публикации (в формате datetime)
имя автора материала
ссылка на страницу автора материала
комментарии в виде (автор комментария и текст комментария)
Структуру сохраняем в MongoDB
"""

import time
import typing
import datetime

import requests
from urllib.parse import urljoin
from pymongo import MongoClient
import bs4


class GbBlogParse:
    def __init__(self, start_url, collection):
        self.time = time.time()
        self.start_url = start_url
        self.collection = collection
        self.done_urls = set()
        self.tasks = []
        start_task = self.get_task(self.start_url, self.parse_feed)
        self.tasks.append(start_task)
        self.done_urls.add(self.start_url)

    def _get_response(self, url, *args, **kwargs):
        if self.time + 1 < time.time():
            time.sleep(1)
        response = requests.get(url, *args, **kwargs)
        self.time = time.time()
        print(url)
        return response

    def _get_soup(self, url, *args, **kwargs):
        soup = bs4.BeautifulSoup(self._get_response(url, *args, **kwargs).text, "lxml")
        return soup

    def get_task(self, url: str, callback: typing.Callable) -> typing.Callable:
        def task():
            soup = self._get_soup(url)
            return callback(url, soup)

        if url in self.done_urls:
            return lambda *_, **__: None
        self.done_urls.add(url)
        return task

    def task_creator(self, url, tags_list, callback):
        links = set(
            urljoin(url, itm.attrs.get("href"))
            for itm in tags_list
            if itm.attrs.get("href")
        )
        for link in links:
            task = self.get_task(link, callback)
            self.tasks.append(task)

    def parse_feed(self, url, soup):
        ul_pagination = soup.find("ul", attrs={"class": "gb__pagination"})
        self.task_creator(url, ul_pagination.find_all("a"), self.parse_feed)
        post_wrapper = soup.find("div", attrs={"class": "post-items-wrapper"})
        self.task_creator(
            url, post_wrapper.find_all("a", attrs={"class": "post-item__title"}), self.parse_post
        )

    def parse_post(self, url, soup):
        title = soup.find("h1", attrs={"class": "blogpost-title"})
        image = soup.find("img").attrs.get("src")
        post_dt = soup.find("time", attrs={"class": "text-md text-muted m-r-md"}).get("datetime")
        author_tag = soup.find(attrs={"class": "row m-t"})
        author_url = author_tag.find("a").get("href")
        author_name = author_tag.find(attrs={"text-lg"})
        post_comments = self.parse_comments(url, soup.find("comments").get("commentable-id"))
        data = {
            "url": url,
            "title": title.text,
            "image": image,
            "date_time": datetime.datetime.strptime(post_dt, '%Y-%m-%dT%H:%M:%S+03:00'),
            "author_name": author_name.text,
            "author_url": urljoin(url, author_url),
            "comments": post_comments
        }
        return data

    def parse_comments(self, url, post_id):
        url_path = "/api/v2/comments?commentable_type=Post&commentable_id=" + post_id
        response = self._get_response(urljoin(url, url_path))
        comment = response.json()
        return comment

    def run(self):
        for task in self.tasks:
            task_result = task()
            if isinstance(task_result, dict):
                self.save(task_result)

    def save(self, data):
        self.collection.insert_one(data)


if __name__ == "__main__":
    collection = MongoClient()["gb_parse_blogs"]["gb_blog"]
    parser = GbBlogParse("https://gb.ru/posts", collection)
    parser.run()
