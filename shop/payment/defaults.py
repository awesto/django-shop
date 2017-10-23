# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _

from django_fsm import transition, RETURN_VALUE

from shop.models.order import BaseOrder, OrderModel
from .base import PaymentProvider


class ForwardFundPayment(PaymentProvider):
    """
    Provides a simple prepayment payment provider.
    """
    namespace = 'forward-fund-payment'

    def get_payment_request(self, cart, request):
        order = OrderModel.objects.create_from_cart(cart, request)
        order.populate_from_cart(cart, request)
        if order.total == 0:
            order.no_payment_required()
        else:
            order.awaiting_payment()
        order.save()
        thank_you_url = OrderModel.objects.get_latest_url()
        return '$window.location.href="{}";'.format(thank_you_url)


class ManualPaymentWorkflowMixin(object):
    """
    Add this class to `settings.SHOP_ORDER_WORKFLOWS` to mix it into your `OrderModel`.
    It adds all the methods required for state transitions, when used with the
    `ForwardFundPayment` provider from above.
    """
    TRANSITION_TARGETS = {
        'awaiting_payment': _("Awaiting a forward fund payment"),
        'prepayment_deposited': _("Prepayment deposited"),
        'no_payment_required': _("No Payment Required"),
    }

    def __init__(self, *args, **kwargs):
        if not isinstance(self, BaseOrder):
            raise ImproperlyConfigured("class 'ManualPaymentWorkflowMixin' is not of type 'BaseOrder'")

        CancelOrderWorkflowMixin.CANCELABLE_SOURCES.update(['awaiting_payment', 'prepayment_deposited',
                                                            'no_payment_required'])
        super(ManualPaymentWorkflowMixin, self).__init__(*args, **kwargs)

    def is_fully_paid(self):
        return super(ManualPaymentWorkflowMixin, self).is_fully_paid()

    @transition(field='status', source=['created'], target='no_payment_required')
    def no_payment_required(self):
        """
        Signals that an Order can proceed directly, by confirming a payment of value zero.
        """

    @transition(field='status', source=['created'], target='awaiting_payment')
    def awaiting_payment(self):
        """
        Signals that the current Order awaits a payment.
        Invoked by ForwardFundPayment.get_payment_request.
        """

    def deposited_too_little(self):
        return self.amount_paid > 0 and self.amount_paid < self.total

    @transition(field='status', source=['awaiting_payment'], target='awaiting_payment',
                conditions=[deposited_too_little], custom=dict(admin=True, button_name=_("Deposited too little")))
    def prepayment_partially_deposited(self):
        """
        Signals that the current Order received a payment, which was not enough.
        """

    @transition(field='status', source=['awaiting_payment'], target='prepayment_deposited',
                conditions=[is_fully_paid], custom=dict(admin=True, button_name=_("Mark as Paid")))
    def prepayment_fully_deposited(self):
        """
        Signals that the current Order received a payment, which fully covers the requested sum.
        """

    @transition(field='status', source=['prepayment_deposited', 'no_payment_required'],
                custom=dict(auto=True))
    def acknowledge_prepayment(self):
        """
        Acknowledge the payment. This method is invoked automatically.
        """
        self.acknowledge_payment()

    @transition(field='status', source='refund_payment', target=RETURN_VALUE('refund_payment', 'order_canceled'),
                custom=dict(admin=True, button_name=_("Mark as Refunded")))
    def payment_refunded(self):
        """
        Signals that the payment for this Order has been refunded manually.
        """
        return 'refund_payment' if self.amount_paid else 'order_canceled'


class CancelOrderWorkflowMixin(object):
    """
    Add this class to `settings.SHOP_ORDER_WORKFLOWS` to mix it into your `OrderModel`.
    It adds all the methods required for state transitions, to cancel an order.
    """
    CANCELABLE_SOURCES = {'new', 'created', 'payment_confirmed', 'payment_declined'}
    TRANSITION_TARGETS = {
        'refund_payment': _("Refund payment"),
        'order_canceled': _("Order Canceled"),
    }

    def cancelable(self):
        return self.status in self.CANCELABLE_SOURCES

    @transition(field='status', target=RETURN_VALUE(*TRANSITION_TARGETS.keys()),
                conditions=[cancelable], custom=dict(admin=True, button_name=_("Cancel Order")))
    def cancel_order(self):
        """
        Signals that an Order shall be canceled.
        """
        if self.amount_paid:
            self.refund_payment()
        return 'refund_payment' if self.amount_paid else 'order_canceled'
