# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core import exceptions
from django.core.cache import cache
from django.template import RequestContext
from django.template import TemplateDoesNotExist
from django.template.loader import select_template
from django.utils.html import strip_spaces_between_tags
from django.utils.formats import localize
from django.utils.safestring import mark_safe, SafeText
from django.utils.translation import get_language_from_request

from rest_framework import serializers

from shop import app_settings
from shop.models.customer import CustomerModel
from shop.models.order import OrderItemModel
from shop.rest.money import MoneyField


class BaseCustomerSerializer(serializers.ModelSerializer):
    number = serializers.CharField(source='get_number')

    class Meta:
        model = CustomerModel
        fields = ('number', 'first_name', 'last_name', 'email')


class ProductCommonSerializer(serializers.ModelSerializer):
    """
    Common serializer for the Product model, both for the ProductSummarySerializer and the
    ProductDetailSerializer.
    """
    price = serializers.SerializerMethodField()
    availability = serializers.SerializerMethodField()

    def get_price(self, product):
        price = product.get_price(self.context['request'])
        return localize(price)

    def get_availability(self, product):
        return product.get_availability(self.context['request'])

    def render_html(self, product, postfix):
        """
        Return a HTML snippet containing a rendered summary for this product.
        Build a template search path with `postfix` distinction.
        """
        if not self.label:
            msg = "The Product Serializer must be configured using a `label` field."
            raise exceptions.ImproperlyConfigured(msg)
        app_label = product._meta.app_label.lower()
        request = self.context['request']
        cache_key = 'product:{0}|{1}-{2}-{3}-{4}-{5}'.format(product.id, app_label, self.label,
            product.product_model, postfix, get_language_from_request(request))
        content = cache.get(cache_key)
        if content:
            return mark_safe(content)
        params = [
            (app_label, self.label, product.product_model, postfix),
            (app_label, self.label, 'product', postfix),
            ('shop', self.label, 'product', postfix),
        ]
        try:
            template = select_template(['{0}/products/{1}-{2}-{3}.html'.format(*p) for p in params])
        except TemplateDoesNotExist:
            return SafeText("<!-- no such template: '{0}/products/{1}-{2}-{3}.html' -->".format(*params[0]))
        # when rendering emails, we require an absolute URI, so that media can be accessed from
        # the mail client
        absolute_base_uri = request.build_absolute_uri('/').rstrip('/')
        context = RequestContext(request, {'product': product, 'ABSOLUTE_BASE_URI': absolute_base_uri})
        content = strip_spaces_between_tags(template.render(context).strip())
        cache.set(cache_key, content, app_settings.CACHE_DURATIONS['product_html_snippet'])
        return mark_safe(content)


class BaseProductSummarySerializer(ProductCommonSerializer):
    """
    Keep a global reference onto the class implementing ``BaseProductSummarySerializer``.
    There can be only one class instance, because the products summary is the lowest common
    denominator for all products of this shop instance. Otherwise we would be unable to mix
    different polymorphic product types in the Catalog, Cart and Order list views.

    Serialize a summary of the polymorphic Product model, suitable for Catalog List Views,
    Cart List Views and Order List Views.
    """
    product_url = serializers.URLField(source='get_absolute_url', read_only=True)
    product_type = serializers.CharField(read_only=True)
    product_model = serializers.CharField(read_only=True)

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label', 'catalog')
        super(BaseProductSummarySerializer, self).__init__(*args, **kwargs)


class BaseProductDetailSerializer(ProductCommonSerializer):
    """
    Serialize all fields of the Product model, for the products detail view.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label', 'catalog')
        super(BaseProductDetailSerializer, self).__init__(*args, **kwargs)

    def to_representation(self, obj):
        product = super(BaseProductDetailSerializer, self).to_representation(obj)
        # add a serialized representation of the product to the context
        return {'product': dict(product)}


class BaseOrderItemSerializer(serializers.ModelSerializer):
    line_total = MoneyField()
    unit_price = MoneyField()

    class Meta:
        model = OrderItemModel
