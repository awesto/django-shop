# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import operator
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from rest_framework.filters import BaseFilterBackend


class _CMSPagesFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        """
        Restrict queryset to entities which have one ore more relations to one or more CMS pages.
        """
        cms_pages_fields = getattr(view, 'cms_pages_fields', self.cms_pages_fields)
        if not isinstance(cms_pages_fields, (list, tuple)):
            msg = "`cms_pages_fields` must be a list or tuple of fields referring to djangoCMS pages."
            raise ImproperlyConfigured(msg)
        current_page = request.current_page
        if current_page.publisher_is_draft:
            current_page = current_page.publisher_public
        filter_by_cms_page = [Q((field, current_page)) for field in cms_pages_fields]
        queryset = queryset.filter(reduce(operator.or_, filter_by_cms_page)).distinct()
        return queryset


class CMSPagesFilterBackend(type):
    """
    Filter by CMS pages as categories.
    """
    def __new__(cls, cms_pages_fields=('cms_pages',)):
        bases = (_CMSPagesFilterBackend,)
        attrs = {'cms_pages_fields': cms_pages_fields}
        new_class = type(cls.__name__, bases, attrs)
        return new_class
