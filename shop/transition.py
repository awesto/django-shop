# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import AnonymousUser
from django.db import models
from django.http.request import HttpRequest
from django.utils.six.moves.urllib.parse import urlparse
from post_office import mail
from post_office.models import EmailTemplate
from shop.conf import app_settings
from shop.models.order import BaseOrder
from shop.models.notification import Notification
from shop.serializers.delivery import DeliverySerializer
from shop.serializers.order import OrderDetailSerializer
from shop.signals import email_queued


class EmulateHttpRequest(HttpRequest):
    """
    Use this class to emulate a HttpRequest object, when templates must be rendered
    asynchronously, for instance when an email must be generated out of an Order object.
    """
    def __init__(self, customer, stored_request):
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
        self.customer = customer
        self.user = customer.is_anonymous and AnonymousUser or customer.user
        self.current_page = None


def transition_change_notification(order):
    """
    This function shall be called, after an Order object performed a transition change.

    """
    if not isinstance(order, BaseOrder):
        raise TypeError("Object order must inherit from class BaseOrder")
    emails_in_queue = False
    for notification in Notification.objects.filter(transition_target=order.status):
        recipient = notification.get_recipient(order)
        if recipient is None:
            continue

        # emulate a request object which behaves similar to that one, when the customer submitted its order
        emulated_request = EmulateHttpRequest(order.customer, order.stored_request)
        customer_serializer = app_settings.CUSTOMER_SERIALIZER(order.customer)
        render_context = {'request': emulated_request, 'render_label': 'email'}
        order_serializer = OrderDetailSerializer(order, context=render_context)
        language = order.stored_request.get('language')
        context = {
            'customer': customer_serializer.data,
            'order': order_serializer.data,
            'ABSOLUTE_BASE_URI': emulated_request.build_absolute_uri().rstrip('/'),
            'render_language': language,
        }
        try:
            latest_delivery = order.delivery_set.latest()
            context['latest_delivery'] = DeliverySerializer(latest_delivery, context=render_context).data
        except (AttributeError, models.ObjectDoesNotExist):
            pass
        try:
            template = notification.mail_template.translated_templates.get(language=language)
        except EmailTemplate.DoesNotExist:
            template = notification.mail_template
        attachments = {}
        for notiatt in notification.notificationattachment_set.all():
            attachments[notiatt.attachment.original_filename] = notiatt.attachment.file.file
        mail.send(recipient, template=template, context=context,
                  attachments=attachments, render_on_delivery=True)
        emails_in_queue = True
    if emails_in_queue:
        email_queued()
