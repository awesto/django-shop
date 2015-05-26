# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from six import with_metaclass
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_fsm.signals import post_transition
from post_office import mail
from post_office.models import EmailTemplate
from shop.rest import serializers
from . import deferred
from .order import OrderModel


class Notification(with_metaclass(deferred.ForeignKeyBuilder, models.Model)):
    """
    A task executed on receiving a signal.
    """
    name = models.CharField(max_length=50, verbose_name=_("Name"))
    transition_target = models.CharField(max_length=50, verbose_name=_("Event"))
    mail_to = models.PositiveIntegerField(verbose_name=_("Mail to"), null=True, default=None)
    mail_template = models.ForeignKey(EmailTemplate, verbose_name=_("Template"))

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")

    def transition_name(self):
        if not hasattr(self, '_transition_name'):
            try:
                status_field = [f for f in OrderModel._meta.fields if f.name == 'status'].pop()
                transition = [t for t in status_field.get_all_transitions(OrderModel)].pop()
                self._transition_name = OrderModel.get_transition_name(transition.target)
            except IndexError:
                self._transition_name = _("Does not exists")
        return self._transition_name

    def get_recipient(self, order):
        if self.mail_to is None:
            return
        if self.mail_to == 0:
            return order.user.email
        return get_user_model().objects.get(id=self.mail_to).email


def order_event_notification(sender, instance=None, target=None, **kwargs):
    for notification in Notification.objects.filter(transition_target=target):
        recipient = notification.get_recipient(instance)
        if recipient is None:
            continue
        context = serializers.OrderDetailSerializer(instance).data
        mail.send(recipient, template=notification.mail_template, context=context)
        print notification
    pass

post_transition.connect(order_event_notification)
