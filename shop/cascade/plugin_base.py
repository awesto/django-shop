# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models import get_model
from django.core.exceptions import ImproperlyConfigured
from django.forms import widgets
from django.template.loader import select_template
from django.utils.translation import ugettext_lazy as _
from django.utils.module_loading import import_by_path
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.utils import resolve_dependencies
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.plugin_base import CascadePluginBase
from cmsplugin_cascade.link.forms import LinkForm
from shop import settings as shop_settings


class ShopPluginBase(CascadePluginBase):
    module = 'Shop'
    require_parent = False
    allow_children = False


class ShopLinkForm(LinkForm):
    LINK_TYPE_CHOICES = (('cmspage', _("CMS Page")), ('RELOAD_PAGE', _("Reload Page")), ('PURCHASE_NOW', _("Purchase Now")),)


class ShopLinkPluginBase(ShopPluginBase):
    """
    Base plugin if a link must be offered
    """
    form = ShopLinkForm
    fields = (('link_type', 'cms_page'), 'glossary',)

    class Media:
        js = resolve_dependencies('cascade/js/admin/linkplugin.js')

    @classmethod
    def get_link(cls, obj):
        link = obj.glossary.get('link', {})
        if link.get('type') == 'cmspage':
            if 'model' in link and 'pk' in link:
                if not hasattr(obj, '_link_model'):
                    Model = get_model(*link['model'].split('.'))
                    try:
                        obj._link_model = Model.objects.get(pk=link['pk'])
                    except Model.DoesNotExist:
                        obj._link_model = None
                if obj._link_model:
                    return obj._link_model.get_absolute_url()
        else:
            # use the link type as special action keyword
            return link.get('type')

    def get_ring_bases(self):
        bases = super(ShopLinkPluginBase, self).get_ring_bases()
        bases.append('LinkPluginBase')
        return bases


class DialogFormPluginBase(ShopPluginBase):
    """
    Base class for all plugins adding a dialog form to a placeholder field.
    """
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin', 'ProcessStepPlugin',)
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
        if plugin.get_form_class() is None:
            msg = "Can not register plugin class `{}`, since is does not define a `form_class`."
            raise ImproperlyConfigured(msg.format(plugin.__name__))
        plugin_pool.register_plugin(plugin)

    @classmethod
    def get_form_class(cls):
        return getattr(cls, 'form_class', None)

    def __init__(self, *args, **kwargs):
        super(DialogFormPluginBase, self).__init__(*args, **kwargs)
        self.FormClass = import_by_path(self.get_form_class())

    def get_form_data(self, request):
        """
        Returns data to initialize the corresponding dialog form.
        This method must return a dictionary containing either `instance` - a Python object to
        initialize the form class for this plugin, or `initial` - a dictionary containing initial
        form data, or if both are set, values from `initial` override those of `instance`.
        """
        return {}

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{0}/checkout/{1}'.format(shop_settings.APP_LABEL, self.template_leaf_name),
            'shop/checkout/{}'.format(self.template_leaf_name),
        ]
        return select_template(template_names)

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
