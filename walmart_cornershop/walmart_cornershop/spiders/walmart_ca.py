# -*- coding: utf-8 -*-

import scrapy
import json
from ..items import BranchProductItem, ProductItem


class WalmartCaSpider(scrapy.Spider):
    name = 'walmart-ca'
    allowed_domains = ['walmart.ca']
    start_urls = ['https://www.walmart.ca/en/grocery/N-117']

    item_count = 0

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
        # Get department to verify if it is "Grocery"
        department = response.xpath('//nav/ol/li[2]/a/text()').get()
        # Verify if it is a product detail page
        exists = response.xpath('/html/body/script[1]/text()').re_first(r'activeSkuId')

        if exists and department == 'Grocery':
            product = ProductItem()

            # Get data from script and transform it to dictionary
            pattern = r'(?<=\=)(.*);'
            data = response.xpath('/html/body/script[1]/text()').re_first(pattern)
            data_json = json.loads(data)

            # Extract data from dictionary
            product['store'] = 'Walmart'
            sku = data_json['product']['activeSkuId']
            product['sku'] = sku
            product['barcodes'] = data_json['entities']['skus'][sku]['upc']
            product['brand'] = data_json['entities']['skus'][sku]['brand']['name']
            product['name'] = data_json['product']['item']['name']['en']
            product['description'] = data_json['entities']['skus'][sku]['longDescription']
            product['package'] = data_json['product']['item']['description']
            image = []
            images = data_json['entities']['skus'][sku]['images']
            for i in reversed(range(len(images))):
                image += ['https://i5.walmartimages.ca/' + images[i]['large']['url']]
            product['image'] = list(set(image))
            category = 'Grocery'
            categories = data_json['product']['item']['primaryCategories'][0]['hierarchy']
            for i in reversed(range(len(categories))):
                category += '|' + categories[i]['displayName']['en']
            product['category'] = category
            product['url'] = response.url

            yield product

            # Count number of products retrived
            self.item_count += 1
            if self.item_count > 10:
                raise scrapy.exceptions.CloseSpider('You reach the limit.')
