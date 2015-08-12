# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.http.request import HttpRequest
from django.utils.translation import ugettext_lazy as _
from django.utils.six.moves.urllib.parse import urlparse
from django_fsm.signals import post_transition
from post_office import mail
from post_office.models import EmailTemplate
from filer.fields.file import FilerFileField
from .order import OrderModel


class Notification(models.Model):
    """
    A task executed on receiving a signal.
    """
    name = models.CharField(max_length=50, verbose_name=_("Name"))
    transition_target = models.CharField(max_length=50, verbose_name=_("Event"))
    mail_to = models.PositiveIntegerField(verbose_name=_("Mail to"), null=True, blank=True,
                                          default=None)
    mail_template = models.ForeignKey(EmailTemplate, verbose_name=_("Template"),
                            limit_choices_to=Q(language__isnull=True) | Q(language=''))

    class Meta:
        app_label = 'shop'
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


class NotificationAttachment(models.Model):
    notification = models.ForeignKey(Notification)
    attachment = FilerFileField(null=True, blank=True, related_name='email_attachment')

    class Meta:
        app_label = 'shop'


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
            'ABSOLUTE_BASE_URI': emulated_request.build_absolute_uri().rstrip('/'),
        }
        language = instance.stored_request.get('language')
        try:
            template = notification.mail_template.translated_templates.get(language=language)
        except EmailTemplate.DoesNotExist:
            template = notification.mail_template
        attachments = {}
        for notiatt in notification.notificationattachment_set.all():
            attachments[notiatt.attachment.original_filename] = notiatt.attachment.file.file
        mail.send(recipient, template=notification.mail_template, context=context,
                  attachments=attachments, render_on_delivery=True)

post_transition.connect(order_event_notification)
