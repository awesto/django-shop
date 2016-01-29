# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from adminsortable2.admin import SortableAdminMixin
from parler.admin import TranslatableAdmin
from shop.admin.product import CMSPageAsCategoryMixin, ProductImageInline
from myshop.models import SmartCard


@admin.register(SmartCard)
class SmartCardAdmin(SortableAdminMixin, TranslatableAdmin,
                     CMSPageAsCategoryMixin, admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('product_name', 'slug', 'product_code', 'unit_price', 'active',),
        }),
        (_("Translatable Fields"), {
            'fields': ('description',)
        }),
        (_("Properties"), {
            'fields': ('manufacturer', 'storage', 'card_type',)
        }),
    )
    inlines = (ProductImageInline,)
    prepopulated_fields = {'slug': ('product_name',)}
    list_display = ('product_name', 'product_code', 'unit_price', 'active',)
    search_fields = ('product_name',)
