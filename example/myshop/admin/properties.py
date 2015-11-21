# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from myshop.models.properties import Manufacturer, OperatingSystem


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    pass


@admin.register(OperatingSystem)
class OperatingSystemAdmin(admin.ModelAdmin):
    pass
