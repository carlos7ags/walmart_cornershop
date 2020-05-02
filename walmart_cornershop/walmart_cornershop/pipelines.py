# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Product, BranchProduct

class WalmartCornershopPipeline(object):

    def __init__(self):
        engine = create_engine('sqlite:///db.sqlite', echo=True)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, walmart_ca):

        db = self.Session()
        product = Product(**item)

        # Save product to database if sku doesn't exist
        try:
            db.add(product)
            db.commit()

        except:
            db.rollback()
            raise

        finally:
            db.close()

        return item
