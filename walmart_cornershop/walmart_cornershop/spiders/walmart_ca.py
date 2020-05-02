# -*- coding: utf-8 -*-
import scrapy

from ..items import ProductBranchItem, ProductItem


class WalmarCaSpider(scrapy.Spider):
    name = 'walmart-ca'
    allowed_domains = ['walmart.ca']
    start_urls = ['https://www.walmart.ca/en/grocery/N-117']

    def parse(self, response):
        pass
