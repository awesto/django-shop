# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from adminsortable2.admin import SortableAdminMixin
from cms.admin.placeholderadmin import PlaceholderAdminMixin, FrontendEditableAdminMixin
from shop.admin.product import CMSPageAsCategoryMixin, CMSPageFilter
from shop.models.defaults.commodity import Commodity

if settings.USE_I18N:
    from parler.admin import TranslatableAdmin


    @admin.register(Commodity)
    class CommodityAdmin(SortableAdminMixin, TranslatableAdmin, FrontendEditableAdminMixin,
                         PlaceholderAdminMixin, CMSPageAsCategoryMixin, admin.ModelAdmin):
        fieldsets = (
            (None, {
                'fields': ('product_name', 'slug', 'caption',)
            }),
            (_("Common Fields"), {
                'fields': ('product_code', ('unit_price', 'active',), 'show_breadcrumb', 'sample_image'),
            }),
        )
        filter_horizontal = ('cms_pages',)
        list_filter = (CMSPageFilter,)

        def get_prepopulated_fields(self, request, obj=None):
            return {
                'slug': ('product_name',)
            }

else:

    @admin.register(Commodity)
    class CommodityAdmin(SortableAdminMixin, FrontendEditableAdminMixin, PlaceholderAdminMixin,
                         CMSPageAsCategoryMixin, admin.ModelAdmin):
        fields = ('product_name', 'slug',  'caption', 'product_code',
                  ('unit_price', 'active',), 'show_breadcrumb', 'sample_image',)
        filter_horizontal = ('cms_pages',)
        prepopulated_fields = {'slug': ('product_name',)}
