# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core import exceptions
from django.core.cache import cache
from django.template import TemplateDoesNotExist
from django.template.loader import select_template
from django.utils.html import strip_spaces_between_tags
from django.utils import six
from django.utils.safestring import mark_safe, SafeText
from django.utils.translation import get_language_from_request
from rest_framework import serializers
from shop.conf import app_settings
from shop.models.customer import CustomerModel
from shop.models.product import ProductModel
from shop.models.order import OrderItemModel
from shop.rest.money import MoneyField
from shop.rest.filters import CMSPagesFilterBackend

class BaseCustomerSerializer(serializers.ModelSerializer):
    number = serializers.CharField(source='get_number')

    class Meta:
        model = CustomerModel
        fields = ['number', 'first_name', 'last_name', 'email']


class AvailabilitySerializer(serializers.Serializer):
    earliest = serializers.DateTimeField()
    latest = serializers.DateTimeField()
    quantity = serializers.ReadOnlyField()
    sell_short = serializers.BooleanField()
    limited_offer = serializers.BooleanField()


class ProductSerializer(serializers.ModelSerializer):
    """
    Common serializer for our product model.
    """
    price = serializers.SerializerMethodField()
    product_type = serializers.CharField(read_only=True)
    product_model = serializers.CharField(read_only=True)
    product_url = serializers.URLField(source='get_absolute_url', read_only=True)

    class Meta:
        model = ProductModel
        direct_siblings = None
        fields = '__all__'

    def __init__(self, product, *args, **kwargs):
        kwargs.setdefault('label', 'catalog')
        super(ProductSerializer, self).__init__(product, *args, **kwargs)
        if 'view' in kwargs['context'] and 'with_direct_siblings' in kwargs['context'][
                'view'].kwargs and kwargs['context']['view'].kwargs['with_direct_siblings']:
            self.prev, self.next = self.get_object_with_direct_siblings(
                product, kwargs['context']['request'])
            self.request = kwargs['context']['request']
            self.fields['direct_siblings'] = serializers.SerializerMethodField(
                'serializer_direct_siblings')
            self.Meta.direct_siblings = self.prev, self.next

    def serializer_direct_siblings(self, product, previous=None, next=None):
        if self.prev:
            previous = {
                "product_name": self.prev.product_name,
                "slug": self.prev.slug,
                "img_name": self.prev.images.first().original_filename,
                "img_url": self.prev.images.first().url}
        if self.next:
            next = {
                "product_name": self.next.product_name,
                "slug": self.next.slug,
                "img_name": self.next.images.first().original_filename,
                "img_url": self.next.images.first().url}
        return previous, next

    def get_object_with_direct_siblings(self, product, request=None):
        if not request:
            request = self.request

        if not hasattr(self, '_product_direct_siblings'):
            previous = next = None
            filter_siblings = {
                'active': True,
            }
            if hasattr(ProductModel, 'translations'):
                filter_siblings.update(
                    translations__language_code=get_language_from_request(request))
            queryset = ProductModel.objects.filter(**filter_siblings)
            queryset = CMSPagesFilterBackend().filter_queryset(request, queryset, self)
            nb = queryset.count()
            for index, obj in enumerate(queryset):
                if obj.slug == product.slug:
                    if index > 0:
                        previous = queryset[index - 1]
                    if index < (nb - 1):
                        next = queryset[index + 1]
            self._product_direct_siblings = previous, next
        return self._product_direct_siblings

    def get_price(self, product):
        price = product.get_price(self.context['request'])
        # TODO: check if this can be simplified using str(product.get_price(...))
        if six.PY2:
            return u'{:f}'.format(price)
        return '{:f}'.format(price)

    def render_html(self, product, postfix):
        """
        Return a HTML snippet containing a rendered summary for the given product.
        This HTML snippet typically contains a ``<figure>`` element with a sample image
        ``<img src="..." >`` and a ``<figcaption>`` containing a short description of the product.

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
            ('shop', self.label, product.product_model, postfix),
            ('shop', self.label, 'product', postfix),
        ]
        try:
            template = select_template(['{0}/products/{1}-{2}-{3}.html'.format(*p) for p in params])
        except TemplateDoesNotExist:
            return SafeText("<!-- no such template: '{0}/products/{1}-{2}-{3}.html' -->".format(*params[0]))
        # when rendering emails, we require an absolute URI, so that media can be accessed from
        # the mail client
        absolute_base_uri = request.build_absolute_uri('/').rstrip('/')
        context = {'product': product, 'ABSOLUTE_BASE_URI': absolute_base_uri}
        content = strip_spaces_between_tags(template.render(context, request).strip())
        cache.set(cache_key, content, app_settings.CACHE_DURATIONS['product_html_snippet'])
        return mark_safe(content)


class BaseOrderItemSerializer(serializers.ModelSerializer):
    line_total = MoneyField()
    unit_price = MoneyField()
    product_code = serializers.CharField()

    class Meta:
        model = OrderItemModel
