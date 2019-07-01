# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class UserItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = Field()
    url_token = Field()
    name = Field()
    headline = Field()
    description = Field()
    gender = Field()
    business = Field()
    location = Field()
    employment = Field()
    education = Field()


