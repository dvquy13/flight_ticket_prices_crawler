# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FlightTicketPricesCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    airline = scrapy.Field()
    depart_time = scrapy.Field()
    arrive_time = scrapy.Field()
    duration = scrapy.Field()
    price = scrapy.Field()
    direction = scrapy.Field()
    import_time = scrapy.Field()
    crawl_type = scrapy.Field()
