# -*- coding: utf-8 -*-
import scrapy

from ..items import ProductBranchItem, ProductItem


class WalmarCaSpider(scrapy.Spider):
    name = 'walmart-ca'
    allowed_domains = ['walmart.ca']
    start_urls = ['https://www.walmart.ca/en/grocery/N-117']

    def parse(self, response):
        # Get all urls in every page
        urls = response.xpath('*//a/@href').getall()
        for url in urls:
            url = response.urljoin(url)
            yield scrapy.Request(url=url, callback=self.parse_product)

        # Get next page if list of products page
        next_page_url = response.xpath('//*[@id="loadmore"]/@href').get()
        if next_page_url:
            next_page_url = response.urljoin(next_page_url)
            yield scrapy.Request(url=next_page_url, callback=self.parse)

    def parse_product(self, response):
        pass
