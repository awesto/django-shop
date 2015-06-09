# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.settings import SHOP_APP_LABEL
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from adminsortable2.admin import SortableAdminMixin
from polymorphic.admin import PolymorphicParentModelAdmin
from myshop.models.shopmodels import Product
from myshop.models.commodity import Commodity
from myshop.admin.commodity import CommodityAdmin


class ProductTypeListFilter(admin.SimpleListFilter):
    title = _("Product type")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'product_type'

    def lookups(self, request, model_admin):
        return (
            ('textilepanel', _("Textile Panel")),  # TODO get this list from products
            ('commodity', _("Commodity")),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        model = self.value()
        if not model:
            return queryset
        product_type = ContentType.objects.get(app_label=SHOP_APP_LABEL, model=model)
        return queryset.filter(polymorphic_ctype=product_type)


class ProductAdmin(SortableAdminMixin, PolymorphicParentModelAdmin):
    base_model = Product
    child_models = ((Commodity, CommodityAdmin),)
    list_display = ('identifier', 'unit_price', 'legacy_fixed', 'product_type', 'supplier', 'active',)
    list_display_links = ('identifier',)
    search_fields = ('identifier', 'translations__name',)
    list_filter = (ProductTypeListFilter, 'supplier')

    def price(self, obj):
        return obj.unit_price
    price.short_description = _("Gross Price")

admin.site.register(Product, ProductAdmin)
