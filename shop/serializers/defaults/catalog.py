# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers
from rest_framework.fields import empty
from shop.models.cart import CartModel
from shop.rest.money import MoneyField


class AddToCartSerializer(serializers.Serializer):
    """
    By default, this serializer is used by the view class :class:`shop.views.catalog.AddToCartView`,
    which handles the communication from the "Add to Cart" dialog box.

    If a product has variations, which influence the fields in the "Add to Cart" dialog box, then
    this serializer shall be overridden by a customized implementation. Such a customized "*Add to
    Cart*" serializer has to be connected to the ``AddToCartView``. This usually is achieved in
    the projects ``urls.py`` by changing the catalog's routing to:
    ```
    urlpatterns = [
        ...
        url(r'^(?P<slug>[\w-]+)/add-to-cart', AddToCartView.as_view(
            serializer_class=CustomAddToCartSerializer,
        )),
        ...
    ]
    ```
    """
    quantity = serializers.IntegerField(default=1, min_value=1)
    unit_price = MoneyField(read_only=True)
    subtotal = MoneyField(read_only=True)
    product = serializers.IntegerField(read_only=True, help_text="The product's primary key")
    product_code = serializers.CharField(read_only=True, help_text="Exact product code of the cart item")
    extra = serializers.DictField(read_only=True, default={})
    is_in_cart = serializers.BooleanField(read_only=True, default=False)

    def __init__(self, instance=None, data=empty, **kwargs):
        context = kwargs.get('context', {})
        if 'product' in context:
            instance = self.get_instance(context, data, kwargs)
            if data == empty:
                quantity = self.fields['quantity'].default
            else:
                quantity = self.fields['quantity'].to_internal_value(data['quantity'])
            instance.setdefault('quantity', quantity)
            instance.setdefault('subtotal', instance['quantity'] * instance['unit_price'])
            super(AddToCartSerializer, self).__init__(instance, data, context=context)
        else:
            super(AddToCartSerializer, self).__init__(instance, data, **kwargs)

    def get_instance(self, context, data, extra_args):
        """
        Method to store the ordered products in the cart item instance.
        Remember to override this method, if the ``product_code`` is part of the
        variation rather than being part of the product itself.
        """
        product = context['product']
        try:
            cart = CartModel.objects.get_from_request(context['request'])
        except CartModel.DoesNotExist:
            cart = None
        extra = data.get('extra', {}) if data is not empty else {}
        return {
            'product': product.id,
            'product_code': product.product_code,
            'unit_price': product.get_price(context['request']),
            'is_in_cart': bool(product.is_in_cart(cart)),
            'extra': extra,
        }
