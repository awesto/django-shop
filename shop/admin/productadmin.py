#-*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from shop.models.productmodel import Category, OptionGroup, Option

class CategoryAdmin(ModelAdmin):
    pass
admin.site.register(Category, CategoryAdmin)

admin.site.register(Option)
admin.site.register(OptionGroup)
