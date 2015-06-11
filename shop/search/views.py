# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework.mixins import ListModelMixin
from drf_haystack.generics import HaystackGenericAPIView


class SearchView(ListModelMixin, HaystackGenericAPIView):
    """
    A generic view to be used for rendering the result list while searching.
    """
    serializer_class = None

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
