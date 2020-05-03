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

        if len(item.keys())>4:
            # Send product item to database
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

        else:
            # Send product branch item to database
            product_branch = BranchProduct(**item)
            item_exists = db.query(BranchProduct).filter_by(product_id=product_branch.product_id, branch=product_branch.branch).first()
            if item_exists:
                print('Price {} already in DataBase.'.format(product_branch.product_id))
            else:
                try:
                    db.add(product_branch)
                    db.commit()
                    print('Price {} added to DataBase.'.format(product_branch.product_id))

                except:
                    db.rollback()
                    raise

                finally:
                    db.close()

        return item
