# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from bs4 import BeautifulSoup, NavigableString, Tag
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.db import models
from django.db.models import Q
from django.http.request import HttpRequest
from django.template import Context, Template
from django.utils.six.moves.urllib.parse import urlparse
from django.utils.translation import ugettext_lazy as _, override as translation_override, ugettext_noop

from post_office import mail
from post_office.models import Email as OriginalEmail, EmailTemplate
from post_office.compat import smart_text
from post_office.connections import connections

from filer.fields.file import FilerFileField

from shop.conf import app_settings
from shop.models.order import BaseOrder
from shop.models.fields import ChoiceEnum, ChoiceEnumField


def html_to_text(html):
    "Creates a formatted text email message as a string from a rendered html template (page)"
    soup = BeautifulSoup(html, 'html.parser')
    # Ignore anything in head
    body, text = soup.body, []
    for element in body.descendants:
        # We use type and not isinstance since comments, cdata, etc are subclasses that we don't want
        if type(element) == NavigableString:
            parent_tags = (t for t in element.parents if type(t) == Tag)
            hidden = False
            for parent_tag in parent_tags:
                # Ignore any text inside a non-displayed tag
                # We also behave is if scripting is enabled (noscript is ignored)
                # The list of non-displayed tags and attributes from the W3C specs:
                if (parent_tag.name in ('area', 'base', 'basefont', 'datalist', 'head', 'link',
                                        'meta', 'noembed', 'noframes', 'param', 'rp', 'script',
                                        'source', 'style', 'template', 'track', 'title', 'noscript') or
                    parent_tag.has_attr('hidden') or
                    (parent_tag.name == 'input' and parent_tag.get('type') == 'hidden')):
                    hidden = True
                    break
            if hidden:
                continue

            # remove any multiple and leading/trailing whitespace
            string = ' '.join(element.string.split())
            if string:
                if element.parent.name == 'a':
                    a_tag = element.parent
                    # replace link text with the link
                    string = a_tag['href']
                    # concatenate with any non-empty immediately previous string
                    if (    type(a_tag.previous_sibling) == NavigableString and
                            a_tag.previous_sibling.string.strip() ):
                        text[-1] = text[-1] + ' ' + string
                        continue
                elif element.previous_sibling and element.previous_sibling.name == 'a':
                    text[-1] = text[-1] + ' ' + string
                    continue
                elif element.parent.name == 'p':
                    # Add extra paragraph formatting newline
                    string = '\n' + string
                text += [string]
    doc = '\n'.join(text)
    return doc


class Email(OriginalEmail):
    """
    Patch class `post_office.models.Email` which fixes https://github.com/ui/django-post_office/issues/116
    and additionally converts HTML messages into plain text messages.
    """
    class Meta:
        proxy = True

    def prepare_email_message(self):
        if self.template is not None:
            render_language = self.context.get('render_language', settings.LANGUAGE_CODE)
            _context = Context(self.context)
            with translation_override(render_language):
                subject = Template(self.template.subject).render(_context)
                message = Template(self.template.content).render(_context)
                html_message = Template(self.template.html_content).render(_context)
        else:
            subject = smart_text(self.subject)
            message = self.message
            html_message = self.html_message

        connection = connections[self.backend_alias or 'default']

        if html_message:
            if not message:
                message = html_to_text(html_message)
            msg = EmailMultiAlternatives(
                subject=subject, body=message, from_email=self.from_email,
                to=self.to, bcc=self.bcc, cc=self.cc,
                headers=self.headers, connection=connection)
            msg.attach_alternative(html_message, 'text/html')
        else:
            msg = EmailMessage(
                subject=subject, body=message, from_email=self.from_email,
                to=self.to, bcc=self.bcc, cc=self.cc,
                headers=self.headers, connection=connection)

        for attachment in self.attachments.all():
            msg.attach(attachment.name, attachment.file.read(), mimetype=attachment.mimetype or None)
            attachment.file.close()

        self._cached_email_message = msg
        return msg

# Monkey-patch post_office method
OriginalEmail.prepare_email_message = Email.prepare_email_message


class Notify(ChoiceEnum):
    RECIPIENT = 0
    ugettext_noop("Notify.RECIPIENT")
    VENDOR = 1
    ugettext_noop("Notify.VENDOR")
    CUSTOMER = 2
    ugettext_noop("Notify.CUSTOMER")
    NOBODY = 9
    ugettext_noop("Notify.NOBODY")


class Notification(models.Model):
    """
    A task executed on receiving a signal.
    """
    name = models.CharField(
        max_length=50,
        verbose_name=_("Name"),
    )

    transition_target = models.CharField(
        max_length=50,
        verbose_name=_("Event"),
    )

    notify = ChoiceEnumField(
        _("Whom to notify"),
        enum_type=Notify,
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Recipient"),
        null=True,
        limit_choices_to={'is_staff': True},
    )

    mail_template = models.ForeignKey(
        EmailTemplate,
        verbose_name=_("Template"),
        limit_choices_to=Q(language__isnull=True) | Q(language=''),
    )

    class Meta:
        app_label = 'shop'
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        ordering = ['transition_target', 'recipient_id']

    def __str__(self):
        return self.name

    def get_recipient(self, order):
        if self.notify is Notify.RECIPIENT:
            return self.recipient.email
        if self.notify is Notify.CUSTOMER:
            return order.customer.email
        if self.notify is Notify.VENDOR:
            if hasattr(order, 'vendor'):
                return order.vendor.email
            return app_settings.SHOP_VENDOR_EMAIL


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
        self.user = customer.is_anonymous() and AnonymousUser or customer.user
        self.current_page = None


def order_event_notification(sender, instance=None, target=None, **kwargs):
    from shop.serializers.order import OrderDetailSerializer

    if not isinstance(instance, BaseOrder):
        return
    for notification in Notification.objects.filter(transition_target=target):
        recipient = notification.get_recipient(instance)
        if recipient is None:
            continue

        # emulate a request object which behaves similar to that one, when the customer submitted its order
        emulated_request = EmulateHttpRequest(instance.customer, instance.stored_request)
        customer_serializer = app_settings.CUSTOMER_SERIALIZER(instance.customer)
        order_serializer = OrderDetailSerializer(instance, context={'request': emulated_request})
        language = instance.stored_request.get('language')
        context = {
            'customer': customer_serializer.data,
            'data': order_serializer.data,
            'ABSOLUTE_BASE_URI': emulated_request.build_absolute_uri().rstrip('/'),
            'render_language': language,
        }
        try:
            template = notification.mail_template.translated_templates.get(language=language)
        except EmailTemplate.DoesNotExist:
            template = notification.mail_template
        attachments = {}
        for notiatt in notification.notificationattachment_set.all():
            attachments[notiatt.attachment.original_filename] = notiatt.attachment.file.file
        mail.send(recipient, template=template, context=context,
                  attachments=attachments, render_on_delivery=True)
