# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.apps import apps
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.forms import ChoiceField, widgets
from django.template import TemplateDoesNotExist
from django.template.loader import select_template
from django.utils.html import format_html
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _, pgettext_lazy
from django.utils.safestring import mark_safe
from django.utils.encoding import python_2_unicode_compatible

if 'cmsplugin_cascade' not in settings.INSTALLED_APPS:
    raise ImproperlyConfigured("Please add 'cmsplugin_cascade' to your INSTALLED_APPS")

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.plugin_base import CascadePluginBase
from cmsplugin_cascade.link.forms import LinkForm
from cmsplugin_cascade.link.plugin_base import LinkPluginBase, LinkElementMixin
from django_select2.forms import HeavySelect2Widget

from shop.conf import app_settings
from shop.forms.base import DialogFormMixin
from shop.models.cart import CartModel
from shop.models.product import ProductModel


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
    parent_classes = []
    require_parent = False
    ring_plugin = 'ShopLinkPlugin'

    class Media:
        js = ['cascade/js/admin/linkplugin.js', 'shop/js/admin/shoplinkplugin.js']

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


class ShopButtonPluginBase(ShopLinkPluginBase):
    """
    Base plugin for arbitrary buttons used during various checkout pages.
    """
    fields = ('link_content', ('link_type', 'cms_page', 'section',), 'glossary',)

    class Media:
        css = {'all': ('cascade/css/admin/bootstrap.min.css', 'cascade/css/admin/bootstrap-theme.min.css',)}

    @classmethod
    def get_identifier(cls, instance):
        return mark_safe(instance.glossary.get('link_content', ''))


class ProductSelect2Widget(HeavySelect2Widget):
    def render(self, name, value, attrs=None):
        try:
            result = app_settings.PRODUCT_SELECT_SERIALIZER(ProductModel.objects.get(pk=value))
        except (ProductModel.DoesNotExist, ValueError):
            pass
        else:
            self.choices.append((value, result.data['text']),)
        html = super(ProductSelect2Widget, self).render(name, value, attrs=attrs)
        return html


class ProductSelectField(ChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', ProductSelect2Widget(data_view='shop:select-product'))
        super(ProductSelectField, self).__init__(*args, **kwargs)

    def clean(self, value):
        "Since the ProductSelectField does not specify choices by itself, accept any returned value"
        try:
            return int(value)
        except (TypeError, ValueError):
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
        except (KeyError, ValueError, ObjectDoesNotExist):
            pass


class CatalogLinkPluginBase(LinkPluginBase):
    """
    Alternative implementation to ``cmsplugin_cascade.link.DefaultLinkPluginBase`` which adds
    another link type, namely "Product", to set links onto arbitrary products of this shop.
    """
    fields = (('link_type', 'cms_page', 'section', 'product', 'ext_url', 'mail_to',), 'glossary',)
    ring_plugin = 'ShopLinkPlugin'

    class Media:
        css = {'all': ['shop/css/admin/editplugin.css']}
        js = ['shop/js/admin/shoplinkplugin.js']


class DialogFormPluginBase(ShopPluginBase):
    """
    Base class for all plugins adding a dialog form to a placeholder field.
    """
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin', 'ProcessStepPlugin', 'BootstrapPanelPlugin',
        'SegmentPlugin', 'SimpleWrapperPlugin', 'ValidateSetOfFormsPlugin')
    RENDER_CHOICES = [('form', _("Form dialog")), ('summary', _("Static summary"))]

    render_type = GlossaryField(
        widgets.RadioSelect(choices=RENDER_CHOICES),
        label=_("Render as"),
        initial='form',
        help_text=_("A dialog can also be rendered as a box containing a read-only summary."),
    )

    headline_legend = GlossaryField(
        widgets.CheckboxInput(),
        label=_("Headline Legend"),
        initial=True,
        help_text=_("Render a legend inside the dialog's headline."),
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
        plugin_pool.register_plugin(plugin)

    def get_form_class(self, instance):
        try:
            return import_string(self.form_class)
        except AttributeError:
            msg = "Can not register plugin class '{}', since it neither defines 'form_class' " \
                  "nor overrides 'get_form_class()'."
            raise ImproperlyConfigured(msg.format(self.__name__))

    @classmethod
    def get_identifier(cls, instance):
        render_type = instance.glossary.get('render_type')
        render_type = dict(cls.RENDER_CHOICES).get(render_type, '')
        return format_html(pgettext_lazy('get_identifier', "as {}"), render_type)

    def get_form_data(self, context, instance, placeholder):
        """
        Returns data to initialize the corresponding dialog form.
        This method must return a dictionary containing
         * either `instance` - a Python object to initialize the form class for this plugin,
         * or `initial` - a dictionary containing initial form data, or if both are set, values
           from `initial` override those of `instance`.
        """
        if issubclass(self.get_form_class(instance), DialogFormMixin):
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
                '{0}/checkout/{1}'.format(app_settings.APP_LABEL, self.template_leaf_name).format(render_type),
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
        form_data['initial'].update(plugin_id=instance.pk, plugin_order=request._plugin_order)
        bound_form = self.get_form_class(instance)(**form_data)
        context[bound_form.form_name] = bound_form
        context['headline_legend'] = bool(instance.glossary.get('headline_legend', True))
        return self.super(DialogFormPluginBase, self).render(context, instance, placeholder)
