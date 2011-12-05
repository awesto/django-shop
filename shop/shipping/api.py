# -*- coding: utf-8 -*-
from shop.shop_api import ShopAPI
from shop.order_signals import payment_selection
from shop.models.ordermodel import ExtraOrderPriceField
from django.shortcuts import redirect


class ShippingAPI(ShopAPI):
    """
    This object's purpose is to expose an API to the shop system.
    Ideally, shops (Django shop or others) should implement this API, so that
    shipping plugins are interchangeable between systems.

    This implementation is the interface reference for Django Shop

    Methods defined in BaseBackendAPI:
    getOrder(request): Return the Order object for the current shopper
    """
    def add_shipping_costs(self, order, label, value):
        """
        Add shipping costs to the given order, with the given label (text), and
        for the given value.
        Please not that the value *should* be negative (it's a cost).
        """
        # Check if we already have one shipping cost entry
        eopf = ExtraOrderPriceField.objects.filter(order=order,
                                                   is_shipping=True)
        if eopf and len(eopf) >= 1:
            eopf = eopf[0]

        if eopf:
            # Tweak the total (since the value might have changed)
            order.order_total = order.order_total - eopf.value

            # Update the existing fields
            eopf.label = label
            eopf.value = value
            eopf.save()

            # Re-add the shipping costs to the total
            order.order_total = order.order_total + value
            order.save()

        else:
            # In this case, there was no shipping cost already associated with
            # the order - let's simply create a new one (theat should be the
            # default case)
            ExtraOrderPriceField.objects.create(order=order,
                                                label=label,
                                                value=value,
                                                is_shipping=True)
            order.order_total = order.order_total + value
            order.save()

    def finished(self, order):
        """
        A helper for backends, so that they can call this when their job
        is finished i.e. shipping costs are added to the order.
        This will redirect to the "select a payment method" page.
        """
        # Emit the signal to say we're now selecting payment
        payment_selection.send(self, order=order)
        return redirect('checkout_payment')
