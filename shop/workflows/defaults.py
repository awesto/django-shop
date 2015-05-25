# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django_fsm import transition


class PayInAdvanceWorkflowMixin(object):
    """
    This class is added automatically to a model inheriting from `order.BaseOrder`. It adds all
    the methods required for state transitions, when used in a shop with advanced payment.
    """
    def applyme(self):
        # Just a test to deactivate `payment_deposited`.
        return True
    applyme.hint = _("Test if condition can be applied")

    @transition(field='status', source=['created', 'deposited'], target='deposited', conditions=[applyme],
                custom=dict(admin=True))
    def payment_deposited(self):
        #self.orderpayment_set.all()
        print 'payment_deposited'
