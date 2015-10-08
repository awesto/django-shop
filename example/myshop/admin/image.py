# -*- coding: utf-8 -*-
from django.contrib import admin
from adminsortable2.admin import SortableInlineAdminMixin
from myshop.models.product import ProductImage


class ProductImageInline(SortableInlineAdminMixin, admin.StackedInline):
    model = ProductImage
    extra = 1
