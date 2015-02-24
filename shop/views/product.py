# -*- coding: utf-8 -*-
import os
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework import generics
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer, BrowsableAPIRenderer
from rest_framework.response import Response
from shop.models.product import BaseProduct


class ProductSummarySerializer(serializers.ModelSerializer):
    """
    Serialize a subset of the Product model, suitable for list views.
    """
    product_url = serializers.CharField(source='get_absolute_url', read_only=True)
    price = serializers.SerializerMethodField()
    availability = serializers.SerializerMethodField()

    class Meta:
        model = getattr(BaseProduct, 'MaterializedModel')
        fields = ('name', 'identifier', 'product_url', 'price', 'availability',) + getattr(model, 'summary_fields', ())

    def get_price(self, obj):
        return obj.get_price(self.context['request'])

    def get_availability(self, obj):
        return obj.get_availability(self.context['request'])


class ProductRetrieveView(generics.RetrieveAPIView):
    """
    View responsible for rendering the products summary as shown in products lists, cart lists
    and order item lists.
    """
    serializer_class = ProductSummarySerializer
    # TemplateHTMLRenderer, 
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    def get_object(self):
        assert self.lookup_url_kwarg in self.kwargs
        filter_kwargs = {self.lookup_field: self.kwargs[self.lookup_url_kwarg]}
        queryset = getattr(BaseProduct, 'MaterializedModel').objects
        queryset = queryset.filter(self.limit_choices_to, **filter_kwargs)
        product = get_object_or_404(queryset)
        self.product = product
        return product

    def get_template_names(self):
        app_label = self.product._meta.app_label.lower()
        basename = '{}-summary.html'.format(self.product.__class__.__name__.lower())
        return [
            os.path.join(app_label, basename),
            os.path.join(app_label, 'product-summary.html'),
            'shop/product-summary.html',
        ]

    def get(self, request, *args, **kwargs):
        self.limit_choices_to = kwargs.pop('limit_choices_to')
        self.lookup_url_kwarg = kwargs.pop('lookup_url_kwarg')
        self.lookup_field = kwargs.pop('lookup_field')
        kwargs['context'] = self.get_serializer_context()
        return self.retrieve(request, *args, **kwargs)


class ProductListView(generics.ListAPIView):
    serializer_class = ProductSummarySerializer

    def get_queryset(self):
        return getattr(BaseProduct, 'MaterializedModel').objects.filter(self.limit_choices_to)

    def get(self, request, *args, **kwargs):
        self.limit_choices_to = kwargs.pop('limit_choices_to')
        kwargs['context'] = self.get_serializer_context()
        return self.list(request, *args, **kwargs)


class ProductDetailView(DetailView):
    model = getattr(BaseProduct, 'MaterializedModel')

    def get_queryset(self):
        return self.model.objects.filter(active=True)
