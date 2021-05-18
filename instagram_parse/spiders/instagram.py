import json
import datetime
import scrapy
from ..items import TagParseItem, PostParseItem
from ..loaders import TagLoader, PostLoader


class InstagramSpider(scrapy.Spider):
    name = "instagram"
    allowed_domains = ["www.instagram.com", "i.instagram.com"]
    start_urls = ["https://www.instagram.com/accounts/login/"]
    _login_url = "https://www.instagram.com/accounts/login/ajax/"
    _tags_path = "/explore/tags/"
    pagin_post_url = 'https://i.instagram.com/api/v1/tags/'
    ig_app_id = '846219147392650'

    def __init__(self, login, password, tags, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login = login
        self.password = password
        self.tags = tags

    def parse(self, response, *args, **kwargs):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self._login_url,
                method="POST",
                callback=self.parse,
                formdata={"username": self.login, "enc_password": self.password},
                headers={"X-CSRFToken": js_data["config"]["csrf_token"]},
            )
        except AttributeError:
            data = response.json()
            if data['authenticated']:
                for tag in self.tags:
                    yield response.follow(f"{self._tags_path}{tag}/", callback=self.tag_page_parse)
            else:
                yield response.follow(self.start_urls[0], callback=self.parse)

    def tag_page_parse(self, response):
        data = self.js_data_extract(response)
        item = TagParseItem()
        tag_loader = TagLoader(item=item)
        tag_name = data['entry_data']['TagPage'][0]['data']['name']
        token = data["config"]["csrf_token"]
        top_posts = data['entry_data']['TagPage'][0]['data'].pop('top')
        yield from self.post_parse(top_posts, token, tag_name, 'top')
        recent_posts = data['entry_data']['TagPage'][0]['data'].pop('recent')
        yield from self.post_parse(recent_posts, token, tag_name, 'recent')
        tag_loader.add_value("date_parse", datetime.datetime.now())
        tag_loader.add_value("data", data['entry_data']['TagPage'][0]['data'])
        yield tag_loader.load_item()

    def post_parse(self, data, token, tag_name, type_post):
        sections = data.pop('sections')
        for section in sections:
            for media in section['layout_content']['medias']:
                result = {}
                result.update(media['media'])
                result.update(data)
                item = PostParseItem()
                post_loader = PostLoader(item=item)
                post_loader.add_value("date_parse", datetime.datetime.now())
                post_loader.add_value("data", result)
                yield post_loader.load_item()
        if data['more_available'] and (type_post == 'recent'):
            formdata = {"include_persistent": "0",
                        "max_id": data['next_max_id'],
                        "page": str(data['next_page']),
                        "surface": 'grid',
                        "tab": type_post}
            if data['next_media_ids']:
                formdata.update({"next_media_ids": list(map(str, data['next_media_ids']))})
            yield scrapy.FormRequest(
                f'{self.pagin_post_url}{tag_name}/sections/',
                method="POST",
                callback=self.pagination_follow,
                formdata=formdata,
                headers={"X-CSRFToken": token, "X-IG-App-ID": self.ig_app_id},
                meta={'token': token, 'tag_name': tag_name, 'type_post': type_post},
            )

    def pagination_follow(self, response):
        data = response.json()
        token = response.meta['token']
        tag_name = response.meta['tag_name']
        type_post = response.meta['type_post']
        yield from self.post_parse(data, token, tag_name, type_post)


    def js_data_extract(self, response):
        script = response.xpath(
            "//script[contains(text(), 'window._sharedData =')]/text()"
        ).extract_first()
        return json.loads(script.replace("window._sharedData = ", "")[:-1])