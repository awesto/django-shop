# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import operator
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from rest_framework.filters import BaseFilterBackend


class CMSPagesFilterBackend(BaseFilterBackend):
    """
    Filter by CMS pages as categories.
    """
    def filter_queryset(self, request, queryset, view):
        """
        Restrict queryset to entities which have one ore more relations to one or more CMS pages.
        """
        if not isinstance(view.cms_pages_fields, (list, tuple)):
            msg = "A View class using this filter backend must define a list or tuple of `cms_pages_fields`."
            raise ImproperlyConfigured(msg)
        current_page = request.current_page
        if current_page.publisher_is_draft:
            current_page = current_page.publisher_public
        filter_by_cms_page = [Q((field, current_page)) for field in view.cms_pages_fields]
        queryset = queryset.filter(reduce(operator.or_, filter_by_cms_page)).distinct()
        return queryset
