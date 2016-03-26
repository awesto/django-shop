# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.forms import ChoiceField, widgets
from django.template import TemplateDoesNotExist
from django.template.loader import select_template
from django.utils.html import format_html
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _, pgettext_lazy
from django.utils.safestring import mark_safe
from cms.plugin_pool import plugin_pool
from django.utils.encoding import python_2_unicode_compatible
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.plugin_base import CascadePluginBase
from cmsplugin_cascade.link.forms import LinkForm
from cmsplugin_cascade.link.plugin_base import LinkPluginBase, LinkElementMixin
from cmsplugin_cascade.utils import resolve_dependencies
from django_select2.forms import HeavySelect2Widget
from shop import settings as shop_settings
from shop.forms.base import DialogFormMixin
from shop.models.cart import CartModel
from shop.models.product import ProductModel
from shop.rest.serializers import ProductSelectSerializer


class ShopPluginBase(CascadePluginBase):
    module = "Shop"
    require_parent = False
    allow_children = False


@python_2_unicode_compatible
class ShopLinkElementMixin(LinkElementMixin):
    def __str__(self):
        return self.plugin_class.get_identifier(self)


class ShopLinkPluginBase(ShopPluginBase):
    """
    Base plugin for arbitrary buttons used during various checkout pages.
    """
    allow_children = False
    fields = (('link_type', 'cms_page',), 'glossary',)
    glossary_field_map = {'link': ('link_type', 'cms_page',)}
    allow_children = False
    parent_classes = []
    require_parent = False

    class Media:
        js = resolve_dependencies('shop/js/admin/shoplinkplugin.js')

    @classmethod
    def get_link(cls, obj):
        link = obj.glossary.get('link', {})
        if link.get('type') == 'cmspage':
            if 'model' in link and 'pk' in link:
                if not hasattr(obj, '_link_model'):
                    Model = apps.get_model(*link['model'].split('.'))
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


class ShopButtonPluginBase(ShopLinkPluginBase):
    """
    Base plugin for arbitrary buttons used during various checkout pages.
    """
    fields = ('link_content', ('link_type', 'cms_page',), 'glossary',)

    class Media:
        css = {'all': ('cascade/css/admin/bootstrap.min.css', 'cascade/css/admin/bootstrap-theme.min.css',)}
        js = resolve_dependencies('shop/js/admin/shoplinkplugin.js')

    @classmethod
    def get_identifier(cls, instance):
        return mark_safe(instance.glossary.get('link_content', ''))


class HeavySelect2Widget(HeavySelect2Widget):
    def render(self, name, value, attrs=None, choices=None):
        try:
            result = ProductSelectSerializer(ProductModel.objects.get(pk=value))
            choices = ((value, result.data['text']),)
        except ProductModel.DoesNotExist:
            choices = ()
        html = super(HeavySelect2Widget, self).render(name, value, attrs=attrs, choices=choices)
        return html


class ProductSelectField(ChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', HeavySelect2Widget(data_view='shop:select-product'))
        super(ProductSelectField, self).__init__(*args, **kwargs)

    def clean(self, value):
        "Since the ProductSelectField does not specify choices by itself, accept any returned value"
        try:
            return int(value)
        except ValueError:
            pass


class CatalogLinkForm(LinkForm):
    """
    Alternative implementation of `cmsplugin_cascade.TextLinkForm`, which allows to link onto
    the Product model, using its method ``get_absolute_url``.

    Note: In this form class the field ``product`` is missing. It is added later, when the shop's
    Product knows about its materialized model.
    """
    LINK_TYPE_CHOICES = (('cmspage', _("CMS Page")), ('product', _("Product")),
                         ('exturl', _("External URL")), ('email', _("Mail To")),)
    product = ProductSelectField(required=False, label='',
        help_text=_("An internal link onto a product from the shop"))

    def clean_product(self):
        if self.cleaned_data.get('link_type') == 'product':
            app_label = ProductModel._meta.app_label
            self.cleaned_data['link_data'] = {
                'type': 'product',
                'model': '{0}.{1}'.format(app_label, ProductModel.__name__),
                'pk': self.cleaned_data['product'],
            }

    def set_initial_product(self, initial):
        try:
            # check if that product still exists, otherwise return nothing
            Model = apps.get_model(*initial['link']['model'].split('.'))
            initial['product'] = Model.objects.get(pk=initial['link']['pk']).pk
        except (KeyError, ValueError, Model.DoesNotExist):
            pass


class CatalogLinkPluginBase(LinkPluginBase):
    """
    Modified implementation of ``cmsplugin_cascade.link.LinkPluginBase`` which adds link type
    "Product", to set links onto arbitrary products of this shop.
    """
#     glossary_fields = (
#         PartialFormField('title',
#             widgets.TextInput(),
#             label=_("Title"),
#             help_text=_("Link's Title")
#         ),
#     ) + LinkPluginBase.glossary_fields
    glossary_field_map = {'link': ('link_type', 'cms_page', 'product', 'ext_url', 'mail_to',)}

    class Media:
        js = resolve_dependencies('shop/js/admin/shoplinkplugin.js')


class DialogFormPluginBase(ShopPluginBase):
    """
    Base class for all plugins adding a dialog form to a placeholder field.
    """
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin', 'ProcessStepPlugin', 'BootstrapPanelPlugin',
        'SegmentPlugin', 'SimpleWrapperPlugin')
    CHOICES = (('form', _("Form dialog")), ('summary', _("Static summary")),)
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

    @classmethod
    def get_identifier(cls, instance):
        render_type = instance.glossary.get('render_type')
        render_type = dict(cls.CHOICES).get(render_type, '')
        return format_html(pgettext_lazy('get_identifier', "as {}"), render_type)

    def __init__(self, *args, **kwargs):
        super(DialogFormPluginBase, self).__init__(*args, **kwargs)
        self.FormClass = import_string(self.get_form_class())

    def get_form_data(self, context, instance, placeholder):
        """
        Returns data to initialize the corresponding dialog form.
        This method must return a dictionary containing
         * either `instance` - a Python object to initialize the form class for this plugin,
         * or `initial` - a dictionary containing initial form data, or if both are set, values
           from `initial` override those of `instance`.
        """
        if issubclass(self.FormClass, DialogFormMixin):
            try:
                cart = CartModel.objects.get_from_request(context['request'])
                cart.update(context['request'])
            except CartModel.DoesNotExist:
                cart = None
            return {'cart': cart}
        return {}

    def get_render_template(self, context, instance, placeholder):
        render_type = instance.glossary.get('render_type')
        if render_type not in ('form', 'summary',):
            render_type = 'form'
        try:
            template_names = [
                '{0}/checkout/{1}'.format(shop_settings.APP_LABEL, self.template_leaf_name).format(render_type),
                'shop/checkout/{}'.format(self.template_leaf_name).format(render_type),
            ]
            return select_template(template_names)
        except (AttributeError, TemplateDoesNotExist):
            return self.render_template

    def render(self, context, instance, placeholder):
        """
        Return the context to render a DialogFormPlugin
        """
        request = context['request']
        form_data = self.get_form_data(context, instance, placeholder)
        request._plugin_order = getattr(request, '_plugin_order', 0) + 1
        if not isinstance(form_data.get('initial'), dict):
            form_data['initial'] = {}
        form_data['initial'].update(plugin_id=instance.id, plugin_order=request._plugin_order)
        bound_form = self.FormClass(**form_data)
        context[bound_form.form_name] = bound_form
        return super(DialogFormPluginBase, self).render(context, instance, placeholder)
