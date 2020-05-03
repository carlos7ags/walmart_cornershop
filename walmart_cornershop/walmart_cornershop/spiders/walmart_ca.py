# -*- coding: utf-8 -*-

import scrapy
import json
from ..items import BranchProductItem, ProductItem
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst


class WalmartCaSpider(CrawlSpider):
    name = 'walmart_ca'
    allowed_domains = ['walmart.ca']
    start_urls = ['https://www.walmart.ca/en/grocery/N-3852',
        'https://www.walmart.ca/en/grocery/N-3799']
    base_url = 'https://www.walmart.ca/'
    price_api = 'api/product-page/find-in-store?'

    item_count = 0

    rules = {
        Rule(LinkExtractor(allow='en/ip/'), callback='parse_product', follow=True),
        Rule(LinkExtractor(allow='en/grocery'), follow=True)
        }


    def parse_product(self, response):
        # Get department to verify if it is "Grocery"
        department = response.xpath('//nav/ol/li[2]/a/text()').get()
        if department == 'Grocery':

            # Get data from script and transform it to dictionary
            pattern = r'(?<=\=)(.*);'
            data = response.xpath('/html/body/script[1]/text()').re_first(pattern)
            data_json = json.loads(data)
            sku = data_json['product']['activeSkuId']

            # Extract data from dictionary and load it to Item
            l = ItemLoader(item=ProductItem(), response=response)
            l.default_output_processor = TakeFirst()

            l.add_value('store', 'Walmart')
            l.add_value('sku', sku)
            l.add_value('barcodes', str(data_json['entities']['skus'][sku]['upc']))
            l.add_value('brand', data_json['entities']['skus'][sku]['brand']['name'])
            l.add_value('name', data_json['product']['item']['name']['en'])
            l.add_value('description', data_json['entities']['skus'][sku]['longDescription'])
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

            # Count number of products retrived
            self.item_count += 1
            if self.item_count > 500:
                raise scrapy.exceptions.CloseSpider('You reach the objective.')

            # Request price and quantity
            stores = [('latitude=43.6562790&longitude=-79.4354490&lang=en&upc=', 3106),
                        ('latitude=48.4120872&longitude=-89.2413988&lang=en&upc=', 3124)]

            for coord, store_id in stores:
                request = scrapy.Request(self.base_url + self.price_api + coord + sku,
                                         callback=self.parse_price,
                                         cb_kwargs=dict(sku=sku))
                request.cb_kwargs['store'] = store_id
                yield request

            return l.load_item()


    def parse_price(self, response, sku, store):
        data_json = json.loads(response.body)

        if data_json['info'][0]['id'] == store:
            data_price = data_json['info'][0]

            # Extract data from dictionary and load it to Item
            l = ItemLoader(item=BranchProductItem(), response=response)
            l.default_output_processor = TakeFirst()

            l.add_value('product_id', sku)
            l.add_value('branch', store)
            l.add_value('stock', data_price['availableToSellQty'])

            if data_price['availabilityStatus'] != 'NOT_SOLD':
                l.add_value('price', data_price['sellPrice'])
            else:
                l.add_value('price', data_price['availabilityStatus'])

            return l.load_item()

        else:
            print('No es la tienda!!!')
