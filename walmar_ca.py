# -*- coding: utf-8 -*-
import scrapy


class WalmarCaSpider(scrapy.Spider):
    name = 'walmar-ca'
    allowed_domains = ['walmart.ca']
    start_urls = ['http://walmart.ca/']

    def parse(self, response):
        pass
