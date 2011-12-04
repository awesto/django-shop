#-*- coding: utf-8 -*-
from shop.models.ordermodel import OrderExtraInfo, Order
from shop.util.order import get_order_from_request


class ShopAPI(object):
    """
    A base-baseclass for shop APIs.

    Both payment and shipping backends need some common functions from the shop
    interface (for example get_order() is useful in both cases). To reduce code
    duplication, theses common methods are defined here and inherited by shop
    interfaces (DRY)

    Another approach would be to stuff everything here, but I think it opens
    up potential to overbloating this one class.
    This is debatable and relatively easy to change later anyway.

    Define all functions common to both the shipping and the payment shop APIs
    here

    PLEASE: When adding functions here please write a short description of
    them in BaseShippingBackend and BasePaymentBackend, future implementers
    thank you :)
    """
    def get_order(self, request):
        """
        Returns the order object for the current shopper.

        This is called from the backend's views as:
        >>> order = self.shop.getOrder(request)
        """
        # it might seem a bit strange to simply forward the call to a helper,
        # but this avoids exposing the shop's internal workings to module
        # writers
        return get_order_from_request(request)

    def add_extra_info(self, order, text):
        """
        Add an extra info text field to the order
        """
        OrderExtraInfo.objects.create(text=text, order=order)

    def is_order_payed(self, order):
        """Whether the passed order is fully payed or not."""
        return order.is_payed()

    def is_order_completed(self, order):
        return order.is_completed()

    def get_order_total(self, order):
        """The total amount to be charged for passed order"""
        return order.order_total

    def get_order_subtotal(self, order):
        """The total amount to be charged for passed order"""
        return order.order_subtotal

    def get_order_short_name(self, order):
        """
        A short name for the order, to be displayed on the payment processor's
        website. Should be human-readable, as much as possible
        """
        return "%s-%s" % (order.id, order.order_total)

    def get_order_unique_id(self, order):
        """
        A unique identifier for this order. This should be our shop's reference
        number. This is sent back by the payment processor when confirming
        payment, for example.
        """
        return order.id

    def get_order_for_id(self, id):
        """
        Get an order for a given ID. Typically, this would be used when the
        backend receives notification from the transaction processor (i.e.
        paypal ipn), with an attached "invoice ID" or "order ID", which should
        then be used to get the shop's order with this method.
        """
        return Order.objects.get(pk=id)
