# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from functools import reduce
import operator
from distutils.version import LooseVersion

from cms import __version__ as cms_version
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from rest_framework.filters import BaseFilterBackend

CMS_LT_3_4 = LooseVersion(cms_version) < LooseVersion('3.5')

class CMSPagesFilterBackend(BaseFilterBackend):
    """
    Use this backend to only show products assigned to the current page.
    """

    cms_pages_fields = ['cms_pages']

    def _get_filtered_queryset(self, current_page, queryset, cms_pages_fields):
        filter_by_cms_page = (Q((field, current_page)) for field in cms_pages_fields)
        return queryset.filter(reduce(operator.or_, filter_by_cms_page)).distinct()

    def filter_queryset(self, request, queryset, view):
        cms_pages_fields = getattr(view, 'cms_pages_fields', self.cms_pages_fields)
        if not isinstance(cms_pages_fields, (list, tuple)):
            msg = "`cms_pages_fields` must be a list or tuple of fields referring to djangoCMS pages."
            raise ImproperlyConfigured(msg)
        current_page = request.current_page
        if current_page.publisher_is_draft:
            current_page = current_page.publisher_public
        return self._get_filtered_queryset(current_page, queryset, cms_pages_fields)


class RecursiveCMSPagesFilterBackend(CMSPagesFilterBackend):
    """
    Use this backend to show products assigned to the current page or any of its descendants.
    """

    def _get_filtered_queryset(self, current_page, queryset, cms_pages_fields):
        if CMS_LT_3_4:
            pages = current_page.get_descendants(include_self=True)
        else:
            pages=list(current_page.get_descendant_pages().values_list('id', flat=True))
            pages.insert(0, current_page.id)
        filter_by_cms_page = (Q((field + "__in", pages)) for field in self.cms_pages_fields)
        return queryset.filter(reduce(operator.or_, filter_by_cms_page)).distinct()
