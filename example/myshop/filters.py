# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms.widgets import Select
from django.utils.translation import ugettext_lazy as _
import django_filters
from djng.forms import NgModelFormMixin
from djng.styling.bootstrap3.forms import Bootstrap3Form
from .models.manufacturer import Manufacturer
from .models.polymorphic.product import Product


class ManufacturerFilter(django_filters.FilterSet):
    manufacturer = django_filters.ModelChoiceFilter(
        queryset=Manufacturer.objects.all(),
        widget=Select(attrs={'ng-change': 'filterChanged()'}),
        empty_label=_("Any Manufacturer"))

    class Meta:
        model = Product
        form = type(str('FilterForm'), (NgModelFormMixin, Bootstrap3Form), {'scope_prefix': 'filters'})
        fields = ['manufacturer']

    @classmethod
    def get_render_context(cls, request, queryset):
        filter_set = cls()
        # we only want to show manufacturers for products available in the current list view
        filter_field = filter_set.filters['manufacturer'].field
        filter_field.queryset = filter_field.queryset.filter(
            id__in=queryset.values_list('manufacturer_id'))
        return dict(filter_set=filter_set)
