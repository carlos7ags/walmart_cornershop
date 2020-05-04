# -*- coding: utf-8 -*-

import scrapy
import json
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst
from ..items import BranchProductItem, ProductItem



class WalmartCaSpider(CrawlSpider):
    name = 'walmart_ca'
    allowed_domains = ['walmart.ca']
    start_urls = ['https://www.walmart.ca/en/grocery/N-3852',
        'https://www.walmart.ca/en/grocery/N-3799']
    base_url = 'https://www.walmart.ca/'
    price_api = 'api/product-page/find-in-store?'

    rules = {
        # Rule to extract all urls from Grocery sites
        Rule(LinkExtractor(allow='en/grocery')),
        # Rule to call parse_product only in product detail page
        Rule(LinkExtractor(allow='en/ip/'), callback='parse_product', follow=True),
        }


    def parse_product(self, response):
        # Get department to verify if it is "Grocery"
        department = response.xpath('//nav/ol/li[2]/a/text()').get()
        if department == 'Grocery':

            # Get data from script and transform it to json
            pattern = r'(?<=\=)(.*);'
            data = response.xpath('/html/body/script[1]/text()').re_first(pattern)
            data_json = json.loads(data)
            sku = data_json['product']['activeSkuId']
            barcodes = data_json['entities']['skus'][sku]['upc']

            # Extract data from dictionary and load it to Item
            l = ItemLoader(item=ProductItem(), response=response)
            l.default_output_processor = TakeFirst()

            l.add_value('store', 'Walmart')
            l.add_value('sku', sku)
            l.add_value('barcodes', str(barcodes))
            l.add_value('brand', data_json['entities']['skus'][sku]['brand']['name'])
            l.add_value('name', data_json['product']['item']['name']['en'])

            # Fix description since come items has paragraph tag
            description = data_json['entities']['skus'][sku]['longDescription']
            description = description.replace('<p>', '')
            description = description.replace('</p>', '')
            l.add_value('description', description)

            l.add_value('package', data_json['product']['item']['description'])

            image_urls = []
            images = data_json['entities']['skus'][sku]['images']
            for i in reversed(range(len(images))):
                image_urls += ['https://i5.walmartimages.ca/' + images[i]['large']['url']]

            l.add_value('image_urls', str(list(set(image_urls))))

            category = 'Grocery'
            categories = data_json['product']['item']['primaryCategories'][0]['hierarchy']
            for i in reversed(range(len(categories))):
                category += '|' + categories[i]['displayName']['en']
            category = category.replace('Grocery|Grocery', 'Grocery')

            l.add_value('category', category)
            l.add_value('url', response.url)

            # Request price and quantity via API
            branches = [['latitude=43.6562790&longitude=-79.4354490&lang=en&upc=', '3106'],
                            ['latitude=48.4120872&longitude=-89.2413988&lang=en&upc=', '3124']]

            yield scrapy.Request(self.base_url + self.price_api + branches[0][0] + barcodes[0],
                                     callback=self.parse_price,
                                     cb_kwargs={'sku':sku, 'branch':branches[0][1]},
                                     cookies={'walmart.preferredstore':3106, 'defaultNearestStoreId':3106,
                                        'walmart.nearestPostalCode':'M6H4A9'},
                                        meta={'dont_merge_cookies': True},
                                     priority=10)

            yield scrapy.Request(self.base_url + self.price_api + branches[1][0] + barcodes[0],
                                     callback=self.parse_price,
                                     cb_kwargs={'sku':sku, 'branch':branches[1][1]},
                                     cookies={'walmart.preferredstore':3124, 'defaultNearestStoreId':3124,
                                        'walmart.nearestPostalCode':'P7B3Z7'},
                                        meta={'dont_merge_cookies': True},
                                     priority=10)
            yield l.load_item()


    def parse_price(self, response, sku, branch):
        data_json = json.loads(response.body)
        if self.price_api in response.url:
            # Check if in correct store brach:
            if str(data_json['info'][0]['id']) == branch:
                data_price = data_json['info'][0]

                # Extract data from dictionary and load it to Item
                l = ItemLoader(item=BranchProductItem(), response=response)
                l.default_output_processor = TakeFirst()

                l.add_value('product_id', str(sku))
                l.add_value('branch', str(branch))

                if data_price['availabilityStatus'] != 'NOT_SOLD':
                    l.add_value('price', str(data_price['sellPrice']))
                    l.add_value('stock', str(data_price['availableToSellQty']))
                else:
                #    l.add_value('price', data_price['availabilityStatus'])
                    l.add_value('price', 0)
                    l.add_value('stock', 0)

                yield l.load_item()
