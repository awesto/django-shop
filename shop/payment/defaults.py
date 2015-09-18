# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django_fsm import transition
from shop.models.order import OrderModel
from .base import PaymentProvider


class ForwardFundPayment(PaymentProvider):
    """
    Provides a simple prepayment payment provider.
    """
    namespace = 'forward-fund-payment'

    def get_payment_request(self, cart, request):
        order = OrderModel.objects.create_from_cart(cart, request)
        order.awaiting_payment()
        order.save()
        thank_you_url = OrderModel.objects.get_latest_url()
        return '$window.location.href="{}";'.format(thank_you_url)


class PayInAdvanceWorkflowMixin(object):
    """
    Add this class to `settings.SHOP_ORDER_WORKFLOWS` to mix it into your `OrderModel`.
    It adds all the methods required for state transitions, when used with the
    `ForwardFundPayment` provider from above.
    """
    TRANSITION_TARGETS = {
        'awaiting_payment': _("Awaiting a forward fund payment"),
        'prepayment_deposited': _("Prepayment deposited"),
    }

    @transition(field='status', source=['created'], target='awaiting_payment')
    def awaiting_payment(self):
        """
        Signals that an Order awaits payments.
        Invoked by ForwardFundPayment.get_payment_request.
        """
        pass

    def deposited_too_little(self):
        amount_paid = self.get_amount_paid()
        return amount_paid > 0 and amount_paid < self.total

    def deposited_enough(self):
        return self.get_amount_paid() >= self.total

    @transition(field='status', source=['awaiting_payment'], target='awaiting_payment',
        conditions=[deposited_too_little], custom=dict(admin=True, button_name=_("Deposited too little")))
    def payment_partially_deposited(self):
        """Signals that an Order received a payment, which was not enough."""
        pass

    @transition(field='status', source=['awaiting_payment'], target='prepayment_deposited',
        conditions=[deposited_enough], custom=dict(admin=True, button_name=_("Mark as Paid")))
    def payment_fully_deposited(self):
        """Signals that an Order received a payment, which which fully covers the requested sum."""
        pass


class CommissionGoodsWorkflowMixin(object):
    """
    Add this class to `settings.SHOP_ORDER_WORKFLOWS` to mix it into your `OrderModel`.
    It adds all the methods required for state transitions, while picking and packing the
    ordered goods for delivery.
    """
    TRANSITION_TARGETS = {
        'pick_goods': _("Picking goods"),
        'pack_goods': _("Packing goods"),
    }

    @transition(field='status', source=['prepayment_deposited', 'charge_credit_card'],
        target='pick_goods', custom=dict(admin=True, button_name=_("Pick the goods")))
    def pick_goods(self, by=None):
        """Change status to 'pick_goods'."""

    @transition(field='status', source=['pick_goods'],
        target='pack_goods', custom=dict(admin=True, button_name=_("Pack the goods")))
    def pack_goods(self, by=None):
        """Change status to 'pack_goods'."""
