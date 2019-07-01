# -*- coding: utf-8 -*-
import scrapy
import json
from zhihuuser.items import UserItem

class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    start_user = 'excited-vczh'
    user_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit=20'
    use_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'
    detail_url = 'https://api.zhihu.com/people/{detailname}'

    def start_requests(self):
        yield scrapy.Request(self.detail_url.format(detailname=self.start_user), self.parse_user,dont_filter= True)
        yield scrapy.Request(self.user_url.format(user= self.start_user, include= self.use_query,offset = 0),self.parse_followee)

    def parse_user(self, response):
        result = json.loads(response.text)
        item = UserItem()
        for field in item.fields:
            if field in result.keys():
                item[field] = result.get(field)
        yield item
        # 这一段递归是进一步对粉丝进行请求，去掉的话就是单纯的请求轮子哥的全部粉丝
        yield scrapy.Request(self.user_url.format(user=result.get('url_token'), include=self.use_query,offset=0),self.parse_followee)

    def parse_followee(self,response):
        result = json.loads(response.text)
        if 'data' in result.keys():
            for item in result.get('data'):
                yield scrapy.Request(self.detail_url.format(detailname =item.get('url_token')), self.parse_user,dont_filter=True)

        if 'paging' in result.keys() and result.get('paging').get('is_end') == False:
            next = result.get('paging').get('next')
            next_page = 'https://www.zhihu.com/api/v4/members' + next[29:]
            yield scrapy.Request(next_page,self.parse_followee)

