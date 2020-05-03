# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Product, BranchProduct
from scrapy.exceptions import DropItem


class WalmartProductPipeline:

    def __init__(self):
        engine = create_engine('sqlite:///db.sqlite', echo=True)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, walmart_ca):

        db = self.Session()
        product = Product(**item)

        item_exists = db.query(Product).filter_by(sku=product.sku).first()
        if item_exists:
            print('Product {} already in DataBase.'.format(product.sku))
        else:
            try:
                db.add(product)
                db.commit()
                print('Product {} added to DataBase.'.format(product.sku))

            except:
                db.rollback()
                raise

            finally:
                db.close()
        return item
