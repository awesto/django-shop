# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.db import models
from django.shortcuts import get_object_or_404
from django.utils.cache import add_never_cache_headers
from django.utils.translation import get_language_from_request

from rest_framework import generics
from rest_framework import status
from rest_framework import views
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.response import Response

from shop.conf import app_settings
from shop.models.product import ProductModel
from shop.rest.filters import CMSPagesFilterBackend
from shop.rest.money import JSONRenderer
from shop.rest.renderers import ShopTemplateHTMLRenderer, CMSPageRenderer
from shop.serializers.bases import ProductSerializer
from shop.serializers.defaults import AddToCartSerializer


class ProductListView(generics.ListAPIView):
    """
    This view is used to list all products which shall be visible below a certain URL.

    Usage: Add it to the urlpatterns responsible for rendering the catalog's views. The
    file containing this patterns can be referenced by the CMS apphook used by the CMS pages
    responsible for rendering the catalog's list view.
    ```
    urlpatterns = [
        url(r'^$', ProductListView.as_view()),
        url(r'^(?P<slug>[\w-]+)/?$', ProductRetrieveView.as_view()),  # see below
        ...
    ]
    ```

    You may add these attributes to the ``as_view()`` method:

    :param renderer_classes: A list or tuple of REST renderer classes.

    :param product_model: The product model onto which the filter set is applied.

    :param serializer_class: The serializer class used to process the queryset returned
        by the catalog's product list view.

    :param limit_choices_to: Limit the queryset of product models to these choices.

    :param filter_class: A filter set which must be inherit from :class:`django_filters.FilterSet`.
    """

    renderer_classes = (CMSPageRenderer, JSONRenderer, BrowsableAPIRenderer)
    product_model = ProductModel
    serializer_class = app_settings.PRODUCT_SUMMARY_SERIALIZER
    limit_choices_to = models.Q()
    filter_class = None

    def get(self, request, *args, **kwargs):
        # TODO: we must find a better way to invalidate the cache.
        # Simply adding a no-cache header eventually decreases the performance dramatically.
        response = self.list(request, *args, **kwargs)
        add_never_cache_headers(response)
        return response

    def get_queryset(self):
        qs = self.product_model.objects.filter(self.limit_choices_to)
        # restrict queryset by language
        if hasattr(self.product_model, 'translations'):
            language = get_language_from_request(self.request)
            qs = qs.prefetch_related('translations').filter(translations__language_code=language)
        qs = qs.select_related('polymorphic_ctype')
        return qs


class SyncCatalogView(views.APIView):
    """
    This view is used to synchronize the number items in the cart from using the catalog's list
    view. It is intended for sites, where we don't want having to access the product's detail
    view for adding it to the cart.

    Use Angular directive <ANY shop-sync-catalog-item="..."> on each catalog item to set up
    the communication with this view.

    To the ``urlpatterns`` responsible for the list view, add
    ```
    urlpatterns = [
        ...
        url(r'^sync-catalog$', SyncCatalogView.as_view(
            serializer_class=SyncCatalogSerializer,
        )),
        ...
    ]
    ```
    to the URLs as specified by the merchant's implementation of its catalog list.

    The class ``SyncCatalogSerializer`` must be provided by the merchant implementation.
    """
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)
    product_model = ProductModel
    product_field = 'product'
    serializer_class = None  # must be overridden by SyncCatalogView.as_view()
    filter_class = None  # may be overridden by SyncCatalogView.as_view()
    limit_choices_to = models.Q()

    def get_context(self, request, **kwargs):
        filter_kwargs = {'id': request.data.get('id')}
        if hasattr(self.product_model, 'translations'):
            filter_kwargs.update(translations__language_code=get_language_from_request(self.request))
        queryset = self.product_model.objects.filter(self.limit_choices_to, **filter_kwargs)
        product = get_object_or_404(queryset)
        return {self.product_field: product, 'request': request}

    def get(self, request, *args, **kwargs):
        context = self.get_context(request, **kwargs)
        serializer = self.serializer_class(context=context, **kwargs)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        context = self.get_context(request, **kwargs)
        serializer = self.serializer_class(data=request.data, context=context)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddToCartView(views.APIView):
    """
    Handle the "Add to Cart" dialog on the products detail page.
    """
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)
    product_model = ProductModel
    serializer_class = AddToCartSerializer
    lookup_field = lookup_url_kwarg = 'slug'
    limit_choices_to = models.Q()

    def get_context(self, request, **kwargs):
        assert self.lookup_url_kwarg in kwargs
        filter_kwargs = {self.lookup_field: kwargs.pop(self.lookup_url_kwarg)}
        if hasattr(self.product_model, 'translations'):
            filter_kwargs.update(translations__language_code=get_language_from_request(self.request))
        queryset = self.product_model.objects.filter(self.limit_choices_to, **filter_kwargs)
        product = get_object_or_404(queryset)
        return {'product': product, 'request': request}

    def get(self, request, *args, **kwargs):
        context = self.get_context(request, **kwargs)
        serializer = self.serializer_class(context=context, **kwargs)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        context = self.get_context(request, **kwargs)
        serializer = self.serializer_class(data=request.data, context=context)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductRetrieveView(generics.RetrieveAPIView):
    """
    This view is used to retrieve and render a certain product.

    Usage: Add it to the urlpatterns responsible for rendering the catalog's views. The
    file containing this patterns can be referenced by the CMS apphook ``ProductsListApp``
    and used by the CMS pages responsible for rendering the catalog's list.
    ```
    urlpatterns = [
        url(r'^$', ProductListView.as_view()),  # see above
        url(r'^(?P<slug>[\w-]+)/?$', ProductRetrieveView.as_view()),
        ...
    ]
    ```
    You may add these attributes to the ``as_view()`` method:

    :param renderer_classes: A list or tuple of REST renderer classes.

    :param lookup_field: The model field used to retrieve the product instance.

    :param lookup_url_kwarg: The name of the parsed URL fragment.

    :param serializer_class: The serializer class used to process the queryset returned
        by the catalog's product detail view.

    :param limit_choices_to: Limit the queryset of product models to these choices.
    """

    renderer_classes = (ShopTemplateHTMLRenderer, JSONRenderer, BrowsableAPIRenderer)
    lookup_field = lookup_url_kwarg = 'slug'
    product_model = ProductModel
    serializer_class = ProductSerializer
    limit_choices_to = models.Q()

    def get_template_names(self):
        product = self.get_object()
        app_label = product._meta.app_label.lower()
        basename = '{}-detail.html'.format(product.__class__.__name__.lower())
        return [
            os.path.join(app_label, 'catalog', basename),
            os.path.join(app_label, 'catalog/product-detail.html'),
            'shop/catalog/product-detail.html',
        ]

    def get_renderer_context(self):
        renderer_context = super(ProductRetrieveView, self).get_renderer_context()
        if renderer_context['request'].accepted_renderer.format == 'html':
            # add the product as Python object to the context
            renderer_context['product'] = self.get_object()
        return renderer_context

    def get_object(self):
        if not hasattr(self, '_product'):
            assert self.lookup_url_kwarg in self.kwargs
            filter_kwargs = {self.lookup_field: self.kwargs[self.lookup_url_kwarg]}
            if hasattr(self.product_model, 'translations'):
                filter_kwargs.update(translations__language_code=get_language_from_request(self.request))
            queryset = self.product_model.objects.filter(self.limit_choices_to, **filter_kwargs)
            self._product = get_object_or_404(queryset)
        return self._product


class ProductSelectView(generics.ListAPIView):
    """
    A simple list view, which is used only by the admin backend. It is required to fetch
    the data for rendering the select widget when looking up for a product.
    """
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)
    serializer_class = app_settings.PRODUCT_SELECT_SERIALIZER

    def get_queryset(self):
        term = self.request.GET.get('term', '')
        if len(term) >= 2:
            return ProductModel.objects.select_lookup(term)[:10]
        return ProductModel.objects.all()[:10]


class AddFilterContextMixin(object):
    """
    A mixin to enrich the render context by ``filter`` containing information
    on how to render the filter set, supplied by attribute ``filter_class``.
    """
    def get_renderer_context(self):
        renderer_context = super(AddFilterContextMixin, self).get_renderer_context()
        if self.filter_class and renderer_context['request'].accepted_renderer.format == 'html':
            # restrict filter set to products associated to this CMS page only
            queryset = self.product_model.objects.filter(self.limit_choices_to)
            queryset = CMSPagesFilterBackend().filter_queryset(self.request, queryset, self)
            renderer_context['filter'] = self.filter_class.get_render_context(self.request, queryset)
        return renderer_context
