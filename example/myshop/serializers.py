# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.template import RequestContext
from django.template.base import TemplateDoesNotExist
from django.template.loader import get_template
from django.utils.html import strip_spaces_between_tags
from django.utils.safestring import mark_safe, SafeText
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.fields import empty
from shop.rest.serializers import ProductSummarySerializerBase, ProductDetailSerializerBase
from shop.search.serializers import ProductSearchSerializer as ProductSearchSerializerBase
from .models.product import Product
from .search_indexes import CommodityIndex


class ProductSummarySerializer(ProductSummarySerializerBase):
    body = serializers.SerializerMethodField()
    media = serializers.SerializerMethodField()
    overlay = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'identifier', 'price', 'product_url',
            'product_type', 'product_model', 'body', 'media', 'overlay')

    def get_body(self, product):
        return self.render_html(product, 'body')

    def get_media(self, product):
        return self.render_html(product, 'media')

    def get_overlay(self, product):
        return self.render_html(product, 'overlay')


class ProductDetailSerializer(ProductDetailSerializerBase):
    discounts = serializers.SerializerMethodField()

    class Meta:
        model = Product
        exclude = ('active',)

    def get_discounts(self, product):
        return product.get_discounts(self.context['request'])


class ExtraSerializer(serializers.Serializer):
    running_meters = serializers.FloatField(required=False, read_only=True)
    order_sample = serializers.BooleanField(label=_("Order a sample"), default=False, required=False)
    addable = serializers.BooleanField(default=True, read_only=True)

    def __init__(self, instance=None, data=empty, **kwargs):
        product = kwargs.pop('product', None)
        minimum_running_meters = getattr(product, 'minimum_length', 1)
        if data == empty:
            running_meters = minimum_running_meters
            order_sample = self.fields['order_sample'].default
            addable = True
        else:
            running_meters = data.get('running_meters', minimum_running_meters)
            order_sample = data.get('order_sample', False)
            addable = order_sample or running_meters >= minimum_running_meters
        instance = dict(running_meters=running_meters, order_sample=order_sample, addable=addable)
        super(ExtraSerializer, self).__init__(instance, data, **kwargs)


class ProductSearchSerializer(ProductSearchSerializerBase):
    """
    Serializer to search over all products in this shop
    """
    app_label = settings.SHOP_APP_LABEL.lower()
    overlay = serializers.SerializerMethodField()

    class Meta(ProductSearchSerializerBase.Meta):
        index_classes = (CommodityIndex,)
        fields = ProductSearchSerializerBase.Meta.fields + ('description', 'media', 'overlay')
        field_aliases = {'q': 'text'}

    def get_overlay(self, search_result):
        template = '{}/products/overview-product-overlay.html'.format(self.app_label)
        try:
            template = get_template(template)
        except TemplateDoesNotExist:
            return SafeText()
        request = self.context['request']
        context = RequestContext(request, {'product': search_result.object})
        content = strip_spaces_between_tags(template.render(context).strip())
        return mark_safe(content)


class CommoditySearchSerializer(ProductSearchSerializer):
    class Meta(ProductSearchSerializer.Meta):
        index_classes = (CommodityIndex,)
        field_aliases = {'q': 'autocomplete'}
