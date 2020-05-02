# -*- coding: utf-8 -*-

import scrapy
import json
from ..items import BranchProductItem, ProductItem
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class WalmartCaSpider(CrawlSpider):
    name = 'walmart_ca'
    allowed_domains = ['walmart.ca']
    start_urls = ['https://www.walmart.ca/en/grocery/N-117']
    base_url = 'https://www.walmart.ca/'

    item_count = 0

    rules = [Rule(LinkExtractor(allow='en/ip/'),
                  callback='parse_product', follow=True)]

    def parse_product(self, response):
        # Get department to verify if it is "Grocery"
        department = response.xpath('//nav/ol/li[2]/a/text()').get()
        if department == 'Grocery':
            product = ProductItem()

            # Get data from script and transform it to dictionary
            pattern = r'(?<=\=)(.*);'
            data = response.xpath('/html/body/script[1]/text()').re_first(pattern)
            data_json = json.loads(data)

            # Extract data from dictionary
            product['store'] = 'Walmart'
            sku = data_json['product']['activeSkuId']
            product['sku'] = sku
            product['barcodes'] = str(data_json['entities']['skus'][sku]['upc'])
            product['brand'] = data_json['entities']['skus'][sku]['brand']['name']
            product['name'] = data_json['product']['item']['name']['en']
            product['description'] = data_json['entities']['skus'][sku]['longDescription']
            product['package'] = data_json['product']['item']['description']
            image_urls = []
            images = data_json['entities']['skus'][sku]['images']
            for i in reversed(range(len(images))):
                image_urls += ['https://i5.walmartimages.ca/' + images[i]['large']['url']]
            product['image_urls'] = str(list(set(image_urls)))
            category = 'Grocery'
            categories = data_json['product']['item']['primaryCategories'][0]['hierarchy']
            for i in reversed(range(len(categories))):
                category += '|' + categories[i]['displayName']['en']
            category = category.replace('Grocery|Grocery', 'Grocery')
            product['category'] = str(category)
            product['url'] = response.url

            yield product

            # Count number of products retrived
            self.item_count += 1
            if self.item_count > 10:
                raise scrapy.exceptions.CloseSpider('You reach the limit.')
