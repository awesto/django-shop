# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from project.models import BookProduct
from project.models import CompactDiscProduct

class BookProductAdmin(ModelAdmin):
    pass
admin.site.register(BookProduct, BookProductAdmin)

class CompactDiscProductAdmin(ModelAdmin):
    pass
admin.site.register(CompactDiscProduct, CompactDiscProductAdmin)