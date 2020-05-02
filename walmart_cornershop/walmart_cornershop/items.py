# -*- coding: utf-8 -*-

import scrapy

class ProductItem(scrapy.Item):
    store = scrapy.Field()
    sku = scrapy.Field()
    barcodes = scrapy.Field()
    brand = scrapy.Field()
    name = scrapy.Field()
    description = scrapy.Field()
    package = scrapy.Field()
    image = scrapy.Field()
    category = scrapy.Field()
    url = scrapy.Field()

class BranchProductItem(scrapy.Item):
    product = scrapy.Field()
    branch = scrapy.Field()
    stock = scrapy.Field()
    price = scrapy.Field()
