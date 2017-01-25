# -*- coding: utf-8 -*-
"""
These URL routings are used by the example `polymorphic` as found in the django-SHOP's tutorials.
The difference here is that we added a special serializer class to add smart phones with their
variations to the cart.
"""
from __future__ import unicode_literals

from django.conf.urls import url
from django.db import models

from shop.models.product import ProductModel
from shop.rest.filters import CMSPagesFilterBackend
from shop.search.views import SearchView
from shop.views.catalog import AddToCartView, CMSPageProductListView, ProductRetrieveView

from myshop.filters import ManufacturerFilter
from myshop.serializers import (ProductSummarySerializer, ProductDetailSerializer,
                                AddSmartCardToCartSerializer, AddSmartPhoneToCartSerializer,
                                CatalogSearchSerializer)


class CMSPageSearchView(SearchView):
    def get_renderer_context(self):
        renderer_context = super(CMSPageSearchView, self).get_renderer_context()
        if self.filter_class and renderer_context['request'].accepted_renderer.format == 'html':
            # restrict to products associated to this CMS page only
            backend = CMSPagesFilterBackend()
            queryset = ProductModel.objects.all()
            queryset = backend.filter_queryset(self.request, queryset, self)
            renderer_context['filter'] = self.filter_class.get_render_context(self.request, queryset)
        return renderer_context


class AddFilterContextMixin(object):
    def get_renderer_context(self):
        renderer_context = super(AddFilterContextMixin, self).get_renderer_context()
        if self.filter_class and renderer_context['request'].accepted_renderer.format == 'html':
            # restrict to products associated to this CMS page only
            backend = CMSPagesFilterBackend()
            queryset = self.product_model.objects.all()
            queryset = backend.filter_queryset(self.request, queryset, self)
            renderer_context['filter'] = self.filter_class.get_render_context(self.request, queryset)
        return renderer_context


class CatalogListWrapper(object):
    product_model = ProductModel
    limit_choices_to = models.Q()
    filter_class = None

    @classmethod
    def as_view(cls):
        self = cls()
        self.search_view = CMSPageSearchView.as_view(
            serializer_class=CatalogSearchSerializer,
            filter_class=ManufacturerFilter,
        )
        self.list_view = CMSPageProductListView.as_view(
            serializer_class=ProductSummarySerializer,
            filter_class=ManufacturerFilter,
        )
        return self

    def __call__(self, request):
        if request.GET.get('q'):
            return self.search_view(request)
        return self.list_view(request)


urlpatterns = [
    url(r'^$', CatalogListWrapper.as_view()),
    url(r'^(?P<slug>[\w-]+)/?$', ProductRetrieveView.as_view(
        serializer_class=ProductDetailSerializer,
    )),
    url(r'^(?P<slug>[\w-]+)/add-to-cart', AddToCartView.as_view(
        serializer_class=AddSmartCardToCartSerializer,
    )),
    url(r'^(?P<slug>[\w-]+)/add-smartphone-to-cart', AddToCartView.as_view(
        serializer_class=AddSmartPhoneToCartSerializer,
    )),
]
