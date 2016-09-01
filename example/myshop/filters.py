# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django_filters
from .models.manufacturer import Manufacturer
from .models.polymorphic.product import Product
from .models.polymorphic.smartcard import SmartCard


class ManufacturerFilter(django_filters.FilterSet):
    manufacturer = django_filters.ModelChoiceFilter(queryset=Manufacturer.objects.all())

    class Meta:
        model = Product
        fields = ['manufacturer']

    @classmethod
    def get_render_context(cls, request, queryset):
        """
        We only want to show manufacturers for the list available in the current list view.
        """
        manufacturer_ids = set([i[0] for i in queryset.values_list('manufacturer')])
        return {'manufacturers': Manufacturer.objects.filter(id__in=manufacturer_ids)}


class SmartCardFilter(django_filters.FilterSet):
    speed = django_filters.MethodFilter(action='filter_speed')

    class Meta:
        model = Product
        fields = ['speed']

    def __init__(self, data=None, queryset=None, prefix=None, strict=None):
        super(SmartCardFilter, self).__init__(data=data, queryset=queryset, prefix=prefix, strict=strict)

    @classmethod
    def get_render_context(cls, request, queryset):
        return {'smartcard_speeds': SmartCard.SPEED}

    def filter_speed(self, queryset, value):
        # TODO: there must be a better method for this kind of database JOIN
        # we convert a Product.objects.all()-qs into a SmartCard.objects.all()-qs
        queryset.get_real_instances()
        #queryset = SmartCard.objects.filter(id__in=[id[0] for id in queryset.values_list('id')])
        queryset = queryset.filter(speed=value)
        return queryset
