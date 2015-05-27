# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from six import with_metaclass
from django.contrib.auth import get_user_model
from django.db import models
from django.http.request import HttpRequest
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.utils.six.moves.urllib.parse import urlparse
from django.utils import translation
from django_fsm.signals import post_transition
from post_office import mail
from post_office.models import EmailTemplate
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


class EmulateHttpRequest(HttpRequest):
    """
    Use this class to emulate a HttpRequest object, when templates must be rendered
    asynchronously, for instance when an email must be generated out of an Order object.
    """
    def __init__(self, user, stored_request):
        super(EmulateHttpRequest, self).__init__()
        parsedurl = urlparse(stored_request.get('absolute_base_uri'))
        self.path = self.path_info = parsedurl.path
        self.environ = {}
        self.META['PATH_INFO'] = parsedurl.path
        self.META['SCRIPT_NAME'] = ''
        self.META['HTTP_HOST'] = parsedurl.netloc
        self.META['HTTP_X_FORWARDED_PROTO'] = parsedurl.scheme
        self.META['QUERY_STRING'] = parsedurl.query
        self.META['HTTP_USER_AGENT'] = stored_request.get('user_agent')
        self.META['REMOTE_ADDR'] = stored_request.get('remote_ip')
        self.method = 'GET'
        self.LANGUAGE_CODE = self.COOKIES['django_language'] = stored_request.get('language')
        self.user = user
        self.current_page = None


def order_event_notification(sender, instance=None, target=None, **kwargs):
    from shop.rest import serializers
    for notification in Notification.objects.filter(transition_target=target):
        recipient = notification.get_recipient(instance)
        if recipient is None:
            continue

        # emulate a request object which behaves similar to that one, when the customer submitted its order
        emulated_request = EmulateHttpRequest(instance.user, instance.stored_request)
        order_serializer = serializers.OrderDetailSerializer(instance, context={'request': emulated_request})
        context = {
            'customer': serializers.CustomerSerializer(instance.user).data,
            'data': order_serializer.data,
        }
        request_context = RequestContext(emulated_request, context)
        with translation.override(instance.stored_request.get('language')):
            mail.send(recipient, template=notification.mail_template, context=request_context)

post_transition.connect(order_event_notification)
