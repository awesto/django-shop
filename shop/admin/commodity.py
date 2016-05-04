# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from adminsortable2.admin import SortableAdminMixin
from cms.admin.placeholderadmin import PlaceholderAdminMixin, FrontendEditableAdminMixin
from shop.admin.product import CMSPageAsCategoryMixin
from shop.models.defaults.commodity import Commodity

if settings.USE_I18N:
    from parler.admin import TranslatableAdmin


    @admin.register(Commodity)
    class CommodityAdmin(SortableAdminMixin, TranslatableAdmin, FrontendEditableAdminMixin,
                         PlaceholderAdminMixin, CMSPageAsCategoryMixin, admin.ModelAdmin):
        fieldsets = (
            (None, {
                'fields': ('translated_product_name', 'slug', 'description',)
            }),
            (_("Common Fields"), {
                'fields': ('product_code', ('unit_price', 'active',), 'sample_image',),
            }),
        )
        filter_horizontal = ('cms_pages',)

        def get_prepopulated_fields(self, request, obj=None):
            return {
                'slug': ('translated_product_name',)
            }

else:

    @admin.register(Commodity)
    class CommodityAdmin(SortableAdminMixin, FrontendEditableAdminMixin, PlaceholderAdminMixin,
                         CMSPageAsCategoryMixin, admin.ModelAdmin):
        fields = ('product_name', 'slug',  'description', 'product_code',
                  ('unit_price', 'active',), 'sample_image',)
        filter_horizontal = ('cms_pages',)
        prepopulated_fields = {'slug': ('product_name',)}
