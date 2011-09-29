from django.db import models

from shop.models.productmodel import Product
from shop.util.fields import CurrencyField


class BookProduct(Product):
    isbn = models.CharField(max_length=255)
    number_of_pages = models.IntegerField()


class CompactDiscProduct(Product):
    number_of_tracks = models.IntegerField()


class BaseProduct(models.Model):
    name = models.CharField(max_length=255)
    unit_price = CurrencyField()


class ProductVariation(Product):
    baseproduct = models.ForeignKey(BaseProduct)

    def get_price(self):
        return self.baseproduct.unit_price

    def get_name(self):
        return "%s - %s" % (self.baseproduct.name, self.name,)



