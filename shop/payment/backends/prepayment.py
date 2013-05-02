# -*- coding: utf-8 -*-
from decimal import Decimal
from datetime import date
from django.conf.urls import patterns, url
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render_to_response
from shop.models.ordermodel import Order, OrderPayment
from shop.models.cartmodel import Cart
from shop.util.decorators import on_method, order_required
from shop.order_signals import confirmed


class ForwardFundBackend(object):
    url_namespace = 'advance-payment'
    backend_name = _('Advance payment')
    template = 'shop/advance-payment-notify.html'

    def __init__(self, shop):
        self.shop = shop

    def get_urls(self):
        urlpatterns = patterns('',
            url(r'^$', self.advance_payment_view, name='advance-payment'),
        )
        return urlpatterns

    @on_method(order_required)
    def advance_payment_view(self, request):
        """
        This view displays a note onto which bank account the customer shall
        wire the requested amount. It then confirms the order by by adding
        zero money as the received payment for that order.
        """
        order = self.shop.get_order(request)
        amount = self.shop.get_order_total(order)
        transaction_id = date.today().strftime('%Y') + '%06d' % order.id
        self._create_confirmed_order(order, transaction_id)
        context = RequestContext(request, {'order': order, 'amount': amount,
            'transaction_id': transaction_id, 'next_url': self.shop.get_finished_url()})
        return render_to_response(self.template, context)

    def _create_confirmed_order(self, order, transaction_id):
        """
        Create an order from the current cart but does not mark it as payed.
        Instead mark the order as CONFIRMED only, as somebody manually has to
        check bank account statements and mark the payments.
        """
        OrderPayment.objects.create(order=order, amount=Decimal(0),
            transaction_id=transaction_id, payment_method=self.backend_name)

        # Confirm the current order
        order.status = Order.CONFIRMED
        order.save()

        # empty the related cart
        try:
            cart = Cart.objects.get(pk=order.cart_pk)
            cart.empty()
        except Cart.DoesNotExist:
            pass
        confirmed.send(sender=self, order=order)
