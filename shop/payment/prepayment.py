# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from shop.models.order import OrderModel
from .base import PaymentProvider


class ForwardFundPayment(PaymentProvider):
    """
    Provides a simple prepayment payment provider.
    """
    namespace = 'forward-fund-payment'

    def get_payment_request(self, cart, request):
        order = OrderModel.objects.create_from_cart(cart, request)
        return '$window.location.href="{}";'.format(order.get_absolute_url())
