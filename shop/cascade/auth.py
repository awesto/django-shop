# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.forms import fields
from django.template.loader import select_template
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from shop import settings as shop_settings
from shop.models.auth import get_customer
from cmsplugin_cascade.link.plugin_base import LinkElementMixin
from cmsplugin_cascade.link.forms import LinkForm
from .plugin_base import ShopLinkPluginBase, DialogFormPluginBase


class ShopAuthForm(LinkForm):
    LINK_TYPE_CHOICES = (('cmspage', _("CMS Page")), ('RELOAD_PAGE', _("Reload Page")), ('DO_NOTHING', _("Do Nothing")))
    FORM_TYPE_COICES = (('login', _("Login Form")), ('logout', _("Logout Form")),
        ('login-logout', _("Shared Login/Logout Form")), ('reset', _("Password Forgotten Form")),
        ('change', _("Change Password Form")),)

    form_type = fields.ChoiceField(label=_("Rendered Form"), choices=FORM_TYPE_COICES,
        help_text=_("Select the appropriate form for various authentication purposes."))

    def clean(self):
        cleaned_data = super(ShopAuthForm, self).clean()
        if self.is_valid():
            cleaned_data['glossary'].update(form_type=cleaned_data['form_type'])
        return cleaned_data


class ShopAuthenticationPlugin(ShopLinkPluginBase):
    """
    A placeholder plugin which provides various authentication forms, such as login-, logout-,
    register-, and other forms. They can be added any placeholder using the Cascade framework.
    """
    name = _("Authentication")
    form = ShopAuthForm
    parent_classes = ('BootstrapColumnPlugin',)
    model_mixins = (LinkElementMixin,)
    fields = ('form_type', ('link_type', 'cms_page'), 'glossary',)
    cache = False

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(ShopAuthenticationPlugin, cls).get_identifier(obj)
        content = dict(ShopAuthForm.FORM_TYPE_COICES).get(obj.glossary.get('form_type'))
        return format_html('{0}{1}', identifier, content)

    def get_render_template(self, context, instance, placeholder):
        form_type = instance.glossary.get('form_type')
        template_names = [
            '{}/auth/{}.html'.format(shop_settings.APP_LABEL, form_type),
            'shop/auth/{}.html'.format(form_type),
        ]
        return select_template(template_names)

plugin_pool.register_plugin(ShopAuthenticationPlugin)


class RegisterFormPlugin(DialogFormPluginBase):
    """
    A placeholder plugin which provides a form, so that a customer may register an account.
    """
    name = _("Register Form")
    form_class = 'shop.forms.auth.RegisterForm'

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/auth/register.html'.format(shop_settings.APP_LABEL),
            'shop/auth/register.html',
        ]
        return select_template(template_names)

    def get_form_data(self, request):
        return {'instance': get_customer(request)}

plugin_pool.register_plugin(RegisterFormPlugin)
