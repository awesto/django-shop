# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms.widgets import Select
from django.utils.translation import ugettext_lazy as _
import django_filters
from djng.forms import NgFormValidationMixin
from djng.styling.bootstrap3.forms import Bootstrap3Form
from .models.manufacturer import Manufacturer
from .models.polymorphic.product import Product
from .models.polymorphic.smartcard import SmartCard


class ManufacturerFilter(django_filters.FilterSet):
    manufacturer = django_filters.ModelChoiceFilter(
        queryset=Manufacturer.objects.all(),
        widget=Select(attrs={'ng-change': 'filterChanged()'}),
        empty_label=_("Any Manufacturer"))

    class Meta:
        model = Product
        form = type(str('FilterForm'), (NgFormValidationMixin, Bootstrap3Form), {})
        fields = ['manufacturer']

    @classmethod
    def get_render_context(cls, request, queryset):
        filter_set = cls()
        # we only want to show manufacturers for products available in the current list view
        filter_field = filter_set.filters['manufacturer'].field
        filter_field.queryset =filter_field.queryset.filter(
            id__in=queryset.values_list('manufacturer_id'))
        return dict(filter_set=filter_set)


class SmartCardFilter(django_filters.FilterSet):
    speed = django_filters.MethodFilter(action='filter_speed',
                                        widget=Select(attrs={'ng-change': 'filterChanged()'}))

    class Meta:
        model = Product
        form = type(str('FilterForm'), (NgFormValidationMixin, Bootstrap3Form), {})
        fields = ['speed']

    def __init__(self, data=None, queryset=None, prefix=None, strict=None):
        super(SmartCardFilter, self).__init__(data=data, queryset=queryset, prefix=prefix, strict=strict)
        pass

    @classmethod
    def get_render_context(cls, request, queryset):
        filter_set = cls()
        filter_field = filter_set.filters['speed'].field
        queryset = queryset.instance_of(SmartCard)
        return dict(filter_set=filter_set)

    def filter_speed(self, queryset, name, value):
        choices = SmartCard.SPEED
        # TODO: there must be a better method for this kind of database JOIN
        # we convert a Product.objects.all()-qs into a SmartCard.objects.all()-qs
        queryset.get_real_instances()
        #queryset = SmartCard.objects.filter(id__in=[id[0] for id in queryset.values_list('id')])
        queryset = queryset.filter(speed=value)
        return queryset
