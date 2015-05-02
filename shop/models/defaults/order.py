# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext_lazy as _
from jsonfield.fields import JSONField
from shop.models import order


class Order(order.BaseOrder):
    """Default materialized model for Order"""
    payment_method = JSONField(blank=True, null=True)
    shipping_method = JSONField(blank=True, null=True)
    shipping_address_text = models.TextField(_("Shipping address"), blank=True, null=True,
        help_text=_("Shipping address at the moment of purchase."))
    invoice_address_text = models.TextField(_("Invoice address"), blank=True, null=True,
        help_text=_("Invoice address at the moment of purchase."))
    annotations = JSONField(null=True, blank=True,
        verbose_name=_("Extra Annotations for this order"))

    def populate_from_cart(self, cart, request):
        super(Order, self).populate_from_cart(cart, request)
        self.payment_method = cart.payment_method
        self.shipping_method = cart.shipping_method
        self.shipping_address_text = cart.shipping_address.as_text()
        self.invoice_address_text = cart.shipping_address.as_text()
        annnotation = cart.extras.get('annotation', '')
        self.annotations = [(self.status, annnotation)]


class OrderItem(order.BaseOrderItem):
    """Default materialized model for OrderItem"""
