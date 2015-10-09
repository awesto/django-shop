# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from adminsortable2.admin import SortableAdminMixin
from polymorphic.admin import PolymorphicParentModelAdmin
from reversion import VersionAdmin
from myshop.models.product import Product
from myshop.models.commodity import Commodity
from .commodity import CommodityAdmin


class ProductTypeListFilter(admin.SimpleListFilter):
    title = _("Product type")
    app_label = settings.SHOP_APP_LABEL.lower()

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'product_type'

    def lookups(self, request, model_admin):
        return (
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
        product_type = ContentType.objects.get(app_label=self.app_label, model=model)
        return queryset.filter(polymorphic_ctype=product_type)


class ProductAdmin(SortableAdminMixin, VersionAdmin, PolymorphicParentModelAdmin):
    base_model = Product
    child_models = ((Commodity, CommodityAdmin),)
    list_display = ('identifier', 'unit_price', 'product_type', 'active',)
    list_display_links = ('identifier',)
    search_fields = ('identifier', 'translations__name',)
    list_filter = (ProductTypeListFilter,)
    list_per_page = 250
    list_max_show_all = 1000

    def price(self, obj):
        return obj.unit_price
    price.short_description = _("Gross Price")

admin.site.register(Product, ProductAdmin)
