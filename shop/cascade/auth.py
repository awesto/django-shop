# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms.fields import ChoiceField
from django.template.loader import select_template
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from django.utils.module_loading import import_string
from cms.plugin_pool import plugin_pool
from shop import settings as shop_settings
from cmsplugin_cascade.link.forms import LinkForm
from .plugin_base import ShopLinkPluginBase, ShopLinkElementMixin

AUTH_FORM_TYPES = (
    ('login', _("Login Form")),
    ('login-reset', _("Login & Reset Form")),
    ('logout', _("Logout Form")),
    ('login-logout', _("Shared Login/Logout Form")),
    ('reset', _("Password Reset Form")),
    ('change', _("Change Password Form")),
    ('register-user', _("Register User"), 'shop.forms.auth.RegisterUserForm'),
    ('continue-as-guest', _("Continue as guest")),
)


class ShopAuthForm(LinkForm):
    LINK_TYPE_CHOICES = (('cmspage', _("CMS Page")), ('RELOAD_PAGE', _("Reload Page")), ('DO_NOTHING', _("Do Nothing")))
    form_type = ChoiceField(label=_("Rendered Form"), choices=(ft[:2] for ft in AUTH_FORM_TYPES),
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
    parent_classes = ('BootstrapColumnPlugin',)
    model_mixins = (ShopLinkElementMixin,)
    fields = ('form_type', ('link_type', 'cms_page'), 'glossary',)
    cache = False

    @classmethod
    def get_identifier(cls, instance):
        identifier = super(ShopAuthenticationPlugin, cls).get_identifier(instance)
        content = dict(ft[:2] for ft in AUTH_FORM_TYPES).get(instance.glossary.get('form_type'), _("unknown"))
        return format_html('{0}{1}', identifier, content)

    def get_form(self, request, obj=None, **kwargs):
        kwargs.update(form=ShopAuthForm)
        return super(ShopAuthenticationPlugin, self).get_form(request, obj, **kwargs)

    def get_render_template(self, context, instance, placeholder):
        form_type = instance.glossary.get('form_type')
        template_names = [
            '{}/auth/{}.html'.format(shop_settings.APP_LABEL, form_type),
            'shop/auth/{}.html'.format(form_type),
        ]
        return select_template(template_names)

    def render(self, context, instance, placeholder):
        """
        Return the context to render a DialogFormPlugin
        """
        form_type = instance.glossary.get('form_type')
        if form_type:
            # prevent a malicious database entry to import an ineligible file
            form_type = AUTH_FORM_TYPES[[ft[0] for ft in AUTH_FORM_TYPES].index(form_type)]
            try:
                FormClass = import_string(form_type[2])
            except (ImportError, IndexError):
                # TODO: other unresolvable may need another form name
                context['form_name'] = 'auth_form'
            else:
                context['form_name'] = FormClass.form_name
                context[FormClass.form_name] = FormClass()
        context['action'] = instance.link
        return super(ShopAuthenticationPlugin, self).render(context, instance, placeholder)

plugin_pool.register_plugin(ShopAuthenticationPlugin)
