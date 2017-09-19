# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import OrderedDict

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms import fields, models, widgets
from django.utils.translation import ugettext_lazy as _

from shop.models.notification import Notify, Notification, NotificationAttachment
from shop.models.order import OrderModel


class NotificationAttachmentAdmin(admin.TabularInline):
    model = NotificationAttachment
    extra = 0


class NotificationForm(models.ModelForm):
    notify_recipient = fields.ChoiceField(label=_("Recipient"))

    class Meta:
        model = Notification
        exclude = ['notify', 'recipient']
        widgets = {
            'transition_target': widgets.Select(),
            'notify_recipient': widgets.Select(),
        }

    def __init__(self, *args, **kwargs):
        if kwargs.get('instance'):
            initial = kwargs.get('initial', {})
            if kwargs['instance'].notify is Notify.RECIPIENT:
                initial['notify_recipient'] = kwargs['instance'].recipient_id
            else:
                initial['notify_recipient'] = kwargs['instance'].notify.name
            kwargs.update(initial=initial)
        super(NotificationForm, self).__init__(*args, **kwargs)
        self.fields['transition_target'].widget.choices = self.get_transition_choices()
        self.fields['notify_recipient'].choices = self.get_recipient_choices()

    def get_transition_choices(self):
        choices = OrderedDict()
        for transition in OrderModel.get_all_transitions():
            if transition.target:
                transition_name = OrderModel.get_transition_name(transition.target)
                choices[transition.target] = transition_name
        return choices.items()

    def get_recipient_choices(self):
        """
        Instead of offering one field for the recipient and one for whom to notify, we
        merge staff users with the context dependent recipients.
        """
        choices = [(n.name, str(n)) for n in Notify if n is not Notify.RECIPIENT]
        for user in get_user_model().objects.filter(is_staff=True):
            email = '{0} <{1}>'.format(user.get_full_name(), user.email)
            choices.append((user.id, email))
        return choices

    def save(self, commit=True):
        obj = super(NotificationForm, self).save(commit=commit)
        try:
            obj.recipient = get_user_model().objects.get(pk=self.cleaned_data['notify_recipient'])
            obj.notify = Notify.RECIPIENT
        except (ValueError, get_user_model().DoesNotExist):
            obj.recipient = None
            obj.notify = getattr(Notify, self.cleaned_data['notify_recipient'], Notify.NOBODY)
        return obj


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['name', 'transition_name', 'get_recipient', 'mail_template', 'num_attachments']
    inlines = (NotificationAttachmentAdmin,)
    form = NotificationForm
    save_as = True

    def transition_name(self, obj):
        return OrderModel.get_transition_name(obj.transition_target)
    transition_name.short_description = _("Event")

    def num_attachments(self, obj):
        return obj.notificationattachment_set.count()
    num_attachments.short_description = _("Attachments")

    def get_recipient(self, obj):
        if obj.notify is Notify.RECIPIENT:
            return '{0} <{1}>'.format(obj.recipient.get_full_name(), obj.recipient.email)
        else:
            return str(obj.notify)
    get_recipient.short_description = _("Mail Recipient")
