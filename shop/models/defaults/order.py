# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils.datetime_safe import datetime
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from shop.models import order


class Order(order.BaseOrder):
    """Default materialized model for Order"""
    shipping_address_text = models.TextField(_("Shipping Address"), blank=True, null=True,
        help_text=_("Shipping address at the moment of purchase."))
    billing_address_text = models.TextField(_("Billing Address"), blank=True, null=True,
        help_text=_("Billing address at the moment of purchase."))
    number = models.PositiveIntegerField(_("Order Number"), null=True, default=None, unique=True)

    @cached_property
    def identifier(self):
        return '{0}-{1}'.format(str(self.number)[:4], str(self.number)[4:])

    def set_number(self):
        """
        Set a unique number to identify this Order object. The first 4 digits represent the
        current year. The last five digits represent a zero-padded incremental counter.
        """
        if self.number is None:
            epoch = datetime.now()
            epoch = epoch.replace(epoch.year, 1, 1, 0, 0, 0, 0)
            aggr = Order.objects.filter(number__isnull=False, created_at__gt=epoch).aggregate(models.Max('number'))
            try:
                epoc_number = int(str(aggr['number__max'])[4:]) + 1
                self.number = int('{0}{1:05d}'.format(epoch.year, epoc_number))
            except (KeyError, ValueError):
                # the first order this year
                self.number = int('{0}00001'.format(epoch.year))

    def populate_from_cart(self, cart, request):
        self.shipping_address_text = cart.shipping_address.as_text()
        self.billing_address_text = cart.shipping_address.as_text()
        self.set_number()
        super(Order, self).populate_from_cart(cart, request)
