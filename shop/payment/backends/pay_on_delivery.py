# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from django.http import HttpResponseRedirect
from shop.util.decorators import on_method, shop_login_required


class PayOnDeliveryBackend(object):

    backend_name = "Pay On Delivery"
    url_namespace = "pay-on-delivery"

    def __init__(self, shop):
        self.shop = shop
        # This is the shop reference, it allows this backend to interact with
        # it in a tidy way (look ma', no imports!)

    @on_method(shop_login_required)
    def simple_view(self, request):
        """
        This simple view does nothing but record the "payment" as being
        complete since we trust the delivery guy to collect money, and redirect
        to the success page. This is the most simple case.
        """
        # Get the order object
        the_order = self.shop.get_order(request)
        # Let's mark this as being complete for the full sum in our database
        # Set it as payed (it needs to be payed to the delivery guy, we assume
        # he does his job properly)
        self.shop.confirm_payment(
            the_order, self.shop.get_order_total(the_order), "None",
            self.backend_name)
        return HttpResponseRedirect(self.shop.get_finished_url())

    def get_urls(self):
        urlpatterns = patterns('',
            url(r'^$', self.simple_view, name='pay-on-delivery'),
        )
        return urlpatterns
