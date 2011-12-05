# -*- coding: utf-8 -*-

"""
This file defines the interafces one should implement when either creating a
new payment module or willing to use modules with another shop system.
"""
from decimal import Decimal
from shop.models.ordermodel import OrderPayment
from shop.shop_api import ShopAPI
from django.core.urlresolvers import reverse


class PaymentAPI(ShopAPI):
    """
    This object's purpose is to expose an API to the shop system.
    Ideally, shops (Django shop or others) should implement this API, so that
    payment plugins are interchangeable between systems.

    This implementation is the interface reference for Django Shop

    Don't forget that since plenty of methods are common to both ShopPaymentAPI
    and ShopShippingAPI(), they are defined in the ShopAPI base class!
    """

    #==========================================================================
    # Payment-specific
    #==========================================================================

    def confirm_payment(self, order, amount, transaction_id, payment_method,
                        save=True):
        """
        Marks the specified amount for the given order as payed.
        This allows to hook in more complex behaviors (like saving a history
        of payments in a Payment model)
        The optional save argument allows backends to explicitly not save the
        order yet
        """
        OrderPayment.objects.create(
            order=order,
            # How much was payed with this particular transfer
            amount=Decimal(amount),
            transaction_id=transaction_id,
            payment_method=payment_method)
        # Save is not used in the particular case.

    #==========================================================================
    # URLS
    #==========================================================================
    # Theses simply return URLs to make redirections easier.
    def get_finished_url(self):
        """
        A helper for backends, so that they can call this when their job
        is finished i.e. The payment has been processed from a user perspective
        This will redirect to the "Thanks for your order" page.
        """
        return reverse('thank_you_for_your_order')

    def get_cancel_url(self):
        """
        A helper for backends to let them redirect to a generic "order was
        cancelled" URL of their choosing.
        """
        return reverse('checkout_payment')
