#-*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from shop.models.cartmodel import Cart, CartItem

class CartAdmin(ModelAdmin):
    pass

admin.site.register(Cart, CartAdmin)

class CartItemAdmin(ModelAdmin):
    pass

admin.site.register(CartItem, CartItemAdmin)