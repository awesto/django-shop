# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal
from django.core.exceptions import ImproperlyConfigured
from django.db.models.aggregates import Sum
from django.db.models.functions import Coalesce
from django.utils.timezone import datetime
from shop.conf import app_settings


class Availability(object):
    """
    Contains the currently available quantity for a given product and period.
    """
    def __init__(self, **kwargs):
        """
        :param earliest: Point in time from when this product will be available.
        :param latest: Point in time until this product will be available.
        :param quantity: Number of available items.
        :param delayed: Mark a product as purchasable with delay.
        """
        self.earliest = kwargs.get('earliest', datetime.min)
        self.latest = kwargs.get('latest', datetime.max)
        quantity = kwargs.get('quantity', app_settings.MAX_PURCHASE_QUANTITY)
        self.quantity = min(quantity, app_settings.MAX_PURCHASE_QUANTITY)
        now = datetime.now()
        delayed = now < self.earliest and now + app_settings.SHOP_UPCOMING_AVAILABILITY >= self.earliest and self.quantity
        self.delayed = kwargs.get('delayed', delayed)


class AvailableProductMixin(object):
    """
    Add this mixin class to the product models declaration, wanting to keep track on the
    current amount of products in stock. In comparison to
    :class:`shop.models.mixins.ProductReserveMixin`, this mixin does not reserve items in pending
    carts, causing the possibility of overselling. It thus is suited for products kept in the cart
    for a long period.

    The product class must implement a field named ``quantity`` accepting numerical values.
    """
    def get_availability(self, request):
        """
        Returns the current available quantity for this product.

        If other customers have pending carts containing this same product, the quantity
        is not not adjusted. This may result in someone adding a product to the cart, but
        unable to purchase, because in the meantime, it might has been bought by someone else.
        """
        if not isinstance(getattr(self, 'quantity', None), (int, float, Decimal)):
            msg = "Product model class {product_model} must contain a numeric model field named `quantity`"
            raise ImproperlyConfigured(msg.format(product_model=self.__class__.__name__))
        return Availability(quantity=self.quantity)


class ReserveProductMixin(AvailableProductMixin):
    """
    Add this mixin class to the product models declaration, wanting to keep track on the
    current amount of products in stock substracting the reserved items for this product in pending
    carts. Use this mixin for products kept for a short period until checking out the cart, for
    instance for ticket sales.

    The product class must implement a field named ``quantity`` accepting numerical values.
    """
    def get_availability(self, request):
        """
        Returns the current available quantity for this product.

        If other customers have pending carts containing this same product, the quantity
        is adjusted accordingly. Therefore make sure to invalidate carts, which were not
        converted into an order after a determined period of time. Otherwise the quantity
        returned by this function might be considerably lower, than what it could be.
        """
        from shop.models.cart import CartItemModel

        availability = super(ReserveProductMixin, self).get_availability(request)
        cart_items = CartItemModel.objects.filter(product=self).values('quantity')
        availability.quantity -= cart_items.aggregate(sum=Coalesce(Sum('quantity'), 0))['sum']
        return availability
