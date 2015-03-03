# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import status
from rest_framework import views
from rest_framework.renderers import BrowsableAPIRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from shop.rest.money import JSONRenderer
from shop.rest.serializers import AddToCartSerializer
from shop.rest.renderers import CMSPageRenderer
from shop.models.product import BaseProduct


class ProductListView(generics.ListAPIView):
    renderer_classes = (CMSPageRenderer, JSONRenderer, BrowsableAPIRenderer)
    serializer_class = None
    limit_choices_to = Q()
    template_name = 'shop/products-list.html'

    def get_queryset(self):
        qs = getattr(BaseProduct, 'MaterializedModel').objects.filter(self.limit_choices_to)

        # restrict products for current CMS page
        current_page = self.request._request.current_page
        if current_page.publisher_is_draft:
            current_page = current_page.publisher_public
        qs = qs.filter(cms_pages=current_page)
        return qs

    def paginate_queryset(self, queryset):
        page = super(ProductListView, self).paginate_queryset(queryset)
        self.paginator = page.paginator
        return page

    def get_renderer_context(self):
        renderer_context = super(ProductListView, self).get_renderer_context()
        if renderer_context['request'].accepted_renderer.format == 'html':
            # add the paginator as Python object to the context
            renderer_context['paginator'] = self.paginator
        return renderer_context


class AddToCartView(views.APIView):
    """
    Handle the "Add to Cart" dialog on the products detail page.
    """
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)
    serializer_class = AddToCartSerializer
    lookup_field = lookup_url_kwarg = 'slug'
    limit_choices_to = Q()

    def get_context(self, request, **kwargs):
        assert self.lookup_url_kwarg in kwargs
        filter_kwargs = {self.lookup_field: kwargs.pop(self.lookup_url_kwarg)}
        queryset = getattr(BaseProduct, 'MaterializedModel').objects
        queryset = queryset.filter(self.limit_choices_to, **filter_kwargs)
        product = get_object_or_404(queryset)
        return {'product': product, 'request': request}

    def get(self, request, *args, **kwargs):
        context = self.get_context(request, **kwargs)
        serializer = self.serializer_class(context=context)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        context = self.get_context(request, **kwargs)
        serializer = self.serializer_class(data=request.data, context=context)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductRetrieveView(generics.RetrieveAPIView):
    """
    View responsible for rendering the products details.
    Additionally an extra method as shown in products lists, cart lists
    and order item lists.
    """
    renderer_classes = (CMSPageRenderer, JSONRenderer, BrowsableAPIRenderer)
    lookup_field = lookup_url_kwarg = 'slug'
    serializer_class = None  # must be set by method `as_view()`
    limit_choices_to = Q()

    def get_template_names(self):
        product = self.get_object()
        app_label = product._meta.app_label.lower()
        basename = '{}-detail.html'.format(product.__class__.__name__.lower())
        return [
            os.path.join(app_label, basename),
            os.path.join(app_label, 'product-detail.html'),
            'shop/product-detail.html',
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
            queryset = getattr(BaseProduct, 'MaterializedModel').objects
            queryset = queryset.filter(self.limit_choices_to, **filter_kwargs)
            product = get_object_or_404(queryset)
            self._product = product
        return self._product
