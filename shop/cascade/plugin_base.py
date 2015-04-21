# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.exceptions import ImproperlyConfigured
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _
from django.utils.module_loading import import_by_path
from django.utils.safestring import mark_safe
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.bootstrap3.buttons import ButtonSizeRenderer, ButtonTypeRenderer
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.plugin_base import CascadePluginBase


class ShopPluginBase(CascadePluginBase):
    module = 'Shop'
    require_parent = False
    allow_children = False


class DialogFormPluginBase(ShopPluginBase):
    """
    Base class for all plugins adding a dialog form to a placeholder field.
    """
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin', 'DialogPagePlugin',)
    CHOICES = (('form', _("Form dialog")), ('summary', _("Summary")),)
    glossary_fields = (
        PartialFormField('render_type',
            widgets.RadioSelect(choices=CHOICES),
            label=_("Render as"),
            initial='form',
            help_text=_("A dialog can also be rendered as a box containing a read-only summary."),
        ),
        PartialFormField('stop_on_error',
            widgets.CheckboxInput(),
            label=_("Stop on error"),
            initial=False,
            help_text=_("Activate, if processing shall stop immediately on invalid form data."),
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
        if not getattr(plugin, 'form_class', None):
            msg = "Can not register plugin class `{}`, since is does not define a `form_class`."
            raise ImproperlyConfigured(msg.format(plugin.__name__))
        plugin_pool.register_plugin(plugin)

    def __init__(self, *args, **kwargs):
        super(DialogFormPluginBase, self).__init__(*args, **kwargs)
        self.FormClass = import_by_path(self.form_class)

    def get_form_data(self, request):
        """
        Returns data to initialize the corresponding dialog form.
        This method must return a dictionary containing either `instance` - a Python object to
        initialize the form class for this plugin, or `initial` - a dictionary containing initial
        form data, or if both are set, values from `initial` override those of `instance`.
        """
        return {}

    def render(self, context, instance, placeholder):
        """
        Return the context to render a DialogFormPlugin
        """
        request = context['request']
        form_data = self.get_form_data(request)
        request._plugin_order = getattr(request, '_plugin_order', 0) + 1
        if not isinstance(form_data.get('initial'), dict):
            form_data['initial'] = {}
        form_data['initial'].update(plugin_id=instance.id, plugin_order=request._plugin_order)
        context[self.FormClass.form_name] = self.FormClass(**form_data)
        return super(DialogFormPluginBase, self).render(context, instance, placeholder)


class ButtonPluginBase(ShopPluginBase):
    require_parent = True
    allow_children = False
    text_enabled = True
    tag_type = None
    default_css_class = 'btn'
    default_css_attributes = ('button-type', 'button-size', 'button-options', 'quick-float',)
    glossary_fields = (
        PartialFormField('button-type',
            widgets.RadioSelect(choices=((k, v) for k, v in ButtonTypeRenderer.BUTTON_TYPES.items()),
                                renderer=ButtonTypeRenderer),
            label=_('Button Type'),
            initial='btn-default',
            help_text=_("Display Link using this Button Style")
        ),
        PartialFormField('button-size',
            widgets.RadioSelect(choices=((k, v) for k, v in ButtonSizeRenderer.BUTTON_SIZES.items()),
                                renderer=ButtonSizeRenderer),
            label=_('Button Size'),
            initial='',
            help_text=_("Display Link using this Button Size")
        ),
        PartialFormField('button-options',
            widgets.CheckboxSelectMultiple(choices=(('btn-block', _('Block level')), ('disabled', _('Disabled')),)),
            label=_('Button Options'),
        ),
        PartialFormField('quick-float',
            widgets.RadioSelect(choices=(('', _("Do not float")), ('pull-left', _("Pull left")), ('pull-right', _("Pull right")),)),
            label=_('Quick Float'),
            initial='',
            help_text=_("Float the button to the left or right.")
        ),
    )

    class Media:
        css = {'all': ('cascade/css/admin/bootstrap.min.css', 'cascade/css/admin/bootstrap-theme.min.css',)}

    @classmethod
    def get_identifier(cls, obj):
        return mark_safe(obj.glossary.get('button_content', ''))
