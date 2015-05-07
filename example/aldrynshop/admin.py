# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.db.models import Max
from adminsortable.admin import SortableAdminMixin, SortableInlineAdminMixin
from parler.admin import TranslatableAdmin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin
from shop.admin.order import BaseOrderAdmin
from aldryn_shop.models.shopmodels import Product, Order
from aldryn_shop.models.products import Commodity, CommodityImage


class OrderAdmin(BaseOrderAdmin):
    pass

admin.site.register(Order, OrderAdmin)


class CommodityImageInline(SortableInlineAdminMixin, admin.StackedInline):
    model = CommodityImage
    extra = 1


class CommodityAdmin(TranslatableAdmin, PolymorphicChildModelAdmin):
    base_model = Product
    fieldsets = (
        (None, {
            'fields': ('product_code', ('unit_price', 'active',),)
        }),
        (_("Translatable Fields"), {
            'fields': ('name', 'slug', 'description',)
        }),
        (_("Properties"), {
            'fields': ('cms_pages',),
        })
    )
    filter_horizontal = ('cms_pages',)
    inlines = (CommodityImageInline,)

    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('name',)}

    def save_model(self, request, obj, form, change):
        if not change:
            # since SortableAdminMixin is missing on this class, ordering has to be computed by hand
            max_order = self.base_model.objects.aggregate(max_order=Max('order'))['max_order']
            obj.order = max_order + 1 if max_order else 1
        super(CommodityAdmin, self).save_model(request, obj, form, change)


class ProductAdmin(SortableAdminMixin, PolymorphicParentModelAdmin):
    base_model = Product
    child_models = ((Commodity, CommodityAdmin),)
    list_display = ('product_code', 'unit_price', 'product_type', 'active',)
    list_display_links = ('product_code',)
    search_fields = ('product_code',)

admin.site.register(Product, ProductAdmin)
