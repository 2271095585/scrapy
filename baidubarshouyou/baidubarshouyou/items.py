# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BaidubarshouyouItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    user_name = scrapy.Field()
    game_comment = scrapy.Field()
    comment_time = scrapy.Field()
    game_name = scrapy.Field()
    pass
