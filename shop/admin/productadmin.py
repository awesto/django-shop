#-*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from shop.models.productmodel import Category, Product


class CategoryAdmin(ModelAdmin):
    pass
admin.site.register(Category, CategoryAdmin)

class ProductAdmin(ModelAdmin):
    pass
admin.site.register(Product, ProductAdmin)