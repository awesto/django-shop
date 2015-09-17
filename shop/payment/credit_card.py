# -*- coding: utf-8 -*-
from decimal import Decimal
from datetime import date
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render_to_response
from shop.models.ordermodel import Order, OrderPayment
from shop.models.cartmodel import Cart
from shop.util.decorators import on_method, order_required
from shop.util.order import get_order_from_request
from shop.order_signals import confirmed


@order_required
def setup_view(self, request):
    """
    Setup the credit card payment
    """
    form = None  # some credit card setup form
    return render_to_response(request, "payment/setup_credit_card.html", form=some_form)


def entry_view(self, request):
    '''
    Calls VISA/MASTERCARD API with correct price
    and payment description
    '''
    order = get_order_from_request(request)
    amount = order.get_total()
    return HttpResponseRedirect('https://visa.com/payment', data={'key': 'my_secret_key', 'amount': amount})


def callback_view(request):
    '''
    Receive callback from credit card payment service and complete the order.
    '''
    order = get_order_from_request(request)

    OrderPayment.objects.create(
        order=order,
        amount=request.POST["amount"],
        transaction_id=request.POST["id"],
        payment_method=PaymentBackend.objects.get(url_name="credit_card"))

    order.mark_as_completed()
    clean_cart(request)

    return HttpResponseRedirect(reverse("home"))