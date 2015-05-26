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
        thank_you_url = OrderModel.objects.get_latest_url()
        return '$window.location.href="{}";'.format(thank_you_url)


class PayInAdvanceWorkflowMixin(object):
    """
    Add this class to `settings.SHOP_ORDER_WORKFLOWS` to mix it into your `OrderModel`.
    It adds all the methods required for state transitions, when used with the
    `ForwardFundPayment` provider from above.
    """
    TRANSITION_TARGETS = {
        'deposited': _("Payment fully deposited"),
        'awaiting_payment': _("Awaiting a forward fund payment"),
    }

    @transition(field='status', source=['created'], target='awaiting_payment')
    def awaiting_payment(self):
        """
        Signals that an Order awaits payments.
        Invoked by ForwardFundPayment.get_payment_request.
        """
        pass

    def deposited_too_little(self):
        return self.get_amount_paid() < self.total_sum

    def deposited_enough(self):
        return not self.deposited_too_little()

    @transition(field='status', source=['awaiting_payment'], target='awaiting_payment',
        conditions=[deposited_too_little], custom=dict(admin=True, button_name=_("Partially Paid")))
    def payment_partially_deposited(self):
        """Signals that an Order received a payment, which was not enough."""
        pass

    @transition(field='status', source=['awaiting_payment'], target='deposited',
        conditions=[deposited_enough], custom=dict(admin=True, button_name=_("Mark as Paid")))
    def payment_fully_deposited(self):
        """Signals that an Order received a payment, which which fully covers the requested sum."""
        pass
