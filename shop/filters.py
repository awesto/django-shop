# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django_filters import filters

from djng.forms import fields


class Filter(filters.Filter):
    field_class = fields.Field


class CharFilter(filters.CharFilter):
    field_class = fields.CharField


class BooleanFilter(filters.BooleanFilter):
    field_class = fields.NullBooleanField


class ChoiceFilter(filters.ChoiceFilter):
    field_class = fields.ChoiceField


class TypedChoiceFilter(filters.TypedChoiceFilter):
    field_class = fields.TypedChoiceField


class UUIDFilter(filters.UUIDFilter):
    field_class = fields.UUIDField


class MultipleChoiceFilter(filters.MultipleChoiceFilter):
    field_class = fields.MultipleChoiceField


class TypedMultipleChoiceFilter(filters.TypedMultipleChoiceFilter):
    field_class = fields.TypedMultipleChoiceField


class DateFilter(filters.DateFilter):
    field_class = fields.DateField


class DateTimeFilter(filters.DateTimeFilter):
    field_class = fields.DateTimeField


class TimeFilter(filters.TimeFilter):
    field_class = fields.TimeField


class DurationFilter(filters.DurationFilter):
    field_class = fields.DurationField


class ModelChoiceFilter(filters.ModelChoiceFilter):
    field_class = fields.ModelChoiceField


class ModelMultipleChoiceFilter(filters.ModelMultipleChoiceFilter):
    field_class = fields.ModelMultipleChoiceField


class NumberFilter(filters.NumberFilter):
    field_class = fields.DecimalField


class NumericRangeFilter(filters.NumericRangeFilter):
    """
    TODO: we first must redeclare the RangeField
    """
