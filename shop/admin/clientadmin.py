#-*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from shop.models.clientmodel import Client, Country, Address

class ClientAdmin(ModelAdmin):
    pass
admin.site.register(Client, ClientAdmin)

class CountryAdmin(ModelAdmin):
    pass
    
admin.site.register(Country, CountryAdmin)

class AddressAdmin(ModelAdmin):
    pass
admin.site.register(Address, AddressAdmin)