from django.db import models
from shop.models.productmodel import Product

# Create your models here.

class BookProduct(Product):
    isbn = models.CharField(max_length=255)
    number_of_pages = models.IntegerField()

class CompactDiscProduct(Product):
    number_of_tracks = models.IntegerField()
