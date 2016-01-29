# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from collections import OrderedDict
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _
from shop.models.notification import Notification, NotificationAttachment
from shop.models.order import OrderModel


class NotificationAttachmentAdmin(admin.TabularInline):
    model = NotificationAttachment
    extra = 0


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    USER_CHOICES = (('', _("Nobody")), (0, _("Customer")),)
    list_display = ('name', 'transition_name', 'recipient', 'mail_template', 'num_attachments')
    inlines = (NotificationAttachmentAdmin,)
    save_as = True

    def get_form(self, request, obj=None, **kwargs):
        kwargs.update(widgets={
            'transition_target': widgets.Select(choices=self.get_transition_choices()),
            'mail_to': widgets.Select(choices=self.get_mailto_choices()),
        })
        return super(NotificationAdmin, self).get_form(request, obj, **kwargs)

    def get_transition_choices(self):
        choices = OrderedDict()
        status_field = [f for f in OrderModel._meta.fields if f.name == 'status'].pop()
        for transition in status_field.get_all_transitions(OrderModel):
            if transition.target:
                transition_name = OrderModel.get_transition_name(transition.target)
                choices[transition.target] = transition_name
        return choices.items()

    def get_mailto_choices(self):
        choices = list(self.USER_CHOICES)
        for user in get_user_model().objects.filter(is_staff=True):
            email = '{0} {1} <{2}>'.format(user.first_name, user.last_name, user.email)
            choices.append((user.id, email))
        return choices

    def transition_name(self, obj):
        return OrderModel.get_transition_name(obj.transition_target)
    transition_name.short_description = _("Event")

    def num_attachments(self, obj):
        return obj.notificationattachment_set.count()
    num_attachments.short_description = _("Attachments")

    def recipient(self, obj):
        try:
            if obj.mail_to > 0:
                user = get_user_model().objects.get(id=obj.mail_to, is_staff=True)
                return '{0} {1} <{2}>'.format(user.first_name, user.last_name, user.email)
            else:
                return OrderedDict(self.USER_CHOICES)[obj.mail_to]
        except (get_user_model().DoesNotExist, KeyError):
            return _("Nobody")
