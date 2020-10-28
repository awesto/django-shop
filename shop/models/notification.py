from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from post_office.models import EmailTemplate
from filer.fields.file import FilerFileField
from shop.conf import app_settings
from shop.models.fields import ChoiceEnum, ChoiceEnumField


class Notify(ChoiceEnum):
    RECIPIENT = 0, _("Recipient")
    VENDOR = 1, _("Vendor")
    CUSTOMER = 2, _("Customer")
    NOBODY = 9, _("Nobody")


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
        on_delete=models.CASCADE,
        verbose_name=_("Recipient"),
        null=True,
        limit_choices_to={'is_staff': True},
    )

    mail_template = models.ForeignKey(
        EmailTemplate,
        on_delete=models.CASCADE,
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
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
    )

    attachment = FilerFileField(
        on_delete=models.SET_NULL,
        related_name='email_attachment',
        null=True,
        blank=True,
    )

    class Meta:
        app_label = 'shop'
