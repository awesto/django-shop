# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.six.moves.urllib.parse import urljoin
from shop.models.order import OrderModel
from .base import PaymentProvider


class ForwardFundPayment(PaymentProvider):
    """
    Provides a simple prepayment payment provider.
    """
    namespace = 'forward-fund-payment'

    def get_payment_request(self, cart, request):
        order = OrderModel.objects.create_from_cart(cart, request)
        thank_you_url = urljoin(order.order_page.get_absolute_url(), 'last')
        return '$window.location.href="{}";'.format(thank_you_url)
