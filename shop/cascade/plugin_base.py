# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.exceptions import ImproperlyConfigured
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _
from django.utils.module_loading import import_by_path
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.plugin_base import CascadePluginBase
from shop import settings as shop_settings


class ShopPluginBase(CascadePluginBase):
    module = 'Shop'
    require_parent = False
    allow_children = False


class DialogFormPlugin(ShopPluginBase):
    """
    Base class for all plugins adding a dialog form to a placeholder field.

    Registered plugins derived from `DialogFormPlugin`, require a form class in
    `settings.SHOP_DIALOG_FORMS` named exactly as its plugin class, but without
    ending in `...Plugin`.
    """
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin',)
    CHOICES = (('form', _("Form dialog")), ('summary', _("Summary")),)
    glossary_fields = (
        PartialFormField('render_type',
            widgets.RadioSelect(choices=CHOICES),
            label=_("Render as"),
            initial='form',
            help_text=_("A dialog can also be rendered as a box containing a read-only summary."),
        ),
    )

    @classmethod
    def register_plugin(cls, plugin):
        """
        Register plugins derived from this class with this function instead of
        `plugin_pool.register_plugin`, so that dialog plugins without a corresponding
        form class are not registered.
        """
        if not issubclass(plugin, cls):
            msg = "Can not register plugin class `{}`, since is does not inherit from `{}`."
            raise ImproperlyConfigured(msg.format(plugin.__name__, cls.__name__))
        for form_class in shop_settings.DIALOG_FORMS:
            class_name = form_class.rsplit('.', 1)[1]
            if '{}Plugin'.format(class_name) == plugin.__name__:
                plugin_pool.register_plugin(plugin)
                break

    def __init__(self, *args, **kwargs):
        super(DialogFormPlugin, self).__init__(*args, **kwargs)
        # search for the corresponding form class
        for form_class in shop_settings.DIALOG_FORMS:
            class_name = form_class.rsplit('.', 1)[1]
            if '{}Plugin'.format(class_name) == self.__class__.__name__:
                self.FormClass = import_by_path(form_class)
                break
        else:
            msg = "No corresponding form class could be found for plugin `{}` in settings.DIALOG_FORMS"
            raise ImproperlyConfigured(msg.format(self.__class__.__name__))

    def get_form_data(self, request):
        """
        Returns data to initialize the corresponding dialog form.
        This method must return a dictionary containing either `instance` - a Python object to
        initialize the form class for this plugin, or `initial` - a dictionary containing initial
        form data.
        """
        return {}

    def render(self, context, instance, placeholder):
        form_data = self.get_form_data(context['request'])
        context[self.FormClass.identifier] = self.FormClass(**form_data)
        return super(DialogFormPlugin, self).render(context, instance, placeholder)
