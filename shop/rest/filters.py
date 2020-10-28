from functools import reduce
import operator

from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from rest_framework.filters import BaseFilterBackend


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
        pages = current_page.get_descendants(include_self=True)
        filter_by_cms_page = (Q((field + "__in", pages)) for field in self.cms_pages_fields)
        return queryset.filter(reduce(operator.or_, filter_by_cms_page)).distinct()
