from django.db import models

from shop.models.productmodel import Product


class Book(Product):
    isbn = models.CharField(max_length=255)

