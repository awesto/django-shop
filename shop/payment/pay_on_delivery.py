# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.conf.urls import patterns, url
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from shop.util.decorators import on_method, shop_login_required, order_required
from shop.util.cart import clean_cart
from shop.util.order import get_order_from_request


@shop_login_required
@order_required
def pay_on_delivery(request):
    """
    This simple PaymentBackend has only one view - entry point which does some work
    internally and then redirects to the "successful URL".
    More complicated views should have entry point (where it calls external API)
    and a callback view which will be called by the API with result.
    """
    # Get the order object
    order = get_order_from_request(request)
    # Since we don't know if the money will be really collected mark the order
    # just as CONFIRMED instead of COMPLETED.
    order.mark_as_confirmed()
    clean_cart(request)
    return HttpResponseRedirect(reverse("home"))