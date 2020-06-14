from django.conf import settings
from django.apps import apps
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist, ValidationError
from django.forms import fields, widgets, ModelChoiceField
from django.template import TemplateDoesNotExist
from django.template.loader import select_template
from django.utils.html import format_html
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from entangled.forms import EntangledModelFormMixin, get_related_object

if 'cmsplugin_cascade' not in settings.INSTALLED_APPS:
    raise ImproperlyConfigured("Please add 'cmsplugin_cascade' to your INSTALLED_APPS")

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.plugin_base import CascadePluginBase
from cmsplugin_cascade.link.forms import LinkForm
from cmsplugin_cascade.link.plugin_base import LinkPluginBase
from django_select2.forms import HeavySelect2Widget
from shop.conf import app_settings
from shop.forms.base import DialogFormMixin
from shop.models.cart import CartModel
from shop.models.product import ProductModel


class ShopPluginBase(CascadePluginBase):
    module = "Shop"
    require_parent = False
    allow_children = False


class ProductSelectField(ModelChoiceField):
    widget = HeavySelect2Widget(data_view='shop:select-product')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('queryset', ProductModel.objects.all())
        super().__init__(*args, **kwargs)


class CatalogLinkForm(LinkForm):
    """
    Alternative implementation of `cmsplugin_cascade.link.forms.LinkForm`, which allows to link onto
    the Product model, using its method ``get_absolute_url``.

    Note: In this form class the field ``product`` is missing. It is added later, when the shop's
    Product knows about its materialized model.
    """
    LINK_TYPE_CHOICES = [
        ('cmspage', _("CMS Page")),
        ('product', _("Product")),
        ('download', _("Download File")),
        ('exturl', _("External URL")),
        ('email', _("Mail To")),
    ]

    product = ProductSelectField(
        label=_("Product"),
        required=False,
        help_text=_("An internal link onto a product from the catalog"),
    )

    class Meta:
        entangled_fields = {'glossary': ['product']}

    def clean(self):
        cleaned_data = super().clean()
        link_type = cleaned_data.get('link_type')
        error = None
        if link_type == 'product':
            if cleaned_data['product'] is None:
                error = ValidationError(_("Product to link to is missing."))
                self.add_error('product', error)
        if error:
            raise error
        return cleaned_data


class CatalogLinkPluginBase(LinkPluginBase):
    """
    Alternative implementation to ``cmsplugin_cascade.link.DefaultLinkPluginBase`` which adds
    another link type, namely "Product", to set links onto arbitrary products of this shop.
    """
    ring_plugin = 'ShopLinkPlugin'

    class Media:
        js = ['admin/js/jquery.init.js', 'shop/js/admin/shoplinkplugin.js']

    @classmethod
    def get_link(cls, obj):
        link_type = obj.glossary.get('link_type')
        if link_type == 'product':
            relobj = get_related_object(obj.glossary, 'product')
            if relobj:
                return relobj.get_absolute_url()
        else:
            return super().get_link(obj) or link_type


class DialogPluginBaseForm(EntangledModelFormMixin):
    RENDER_CHOICES = [
        ('form', _("Form dialog")),
        ('summary', _("Static summary")),
    ]

    render_type = fields.ChoiceField(
        choices=RENDER_CHOICES,
        widget=widgets.RadioSelect,
        label=_("Render as"),
        initial='form',
        help_text=_("A dialog can also be rendered as a box containing a read-only summary."),
    )

    headline_legend = fields.BooleanField(
        label=_("Headline Legend"),
        initial=True,
        required=False,
        help_text=_("Render a legend inside the dialog's headline."),
    )

    class Meta:
        entangled_fields = {'glossary': ['render_type', 'headline_legend']}


class DialogFormPluginBase(ShopPluginBase):
    """
    Base class for all plugins adding a dialog form to a placeholder field.
    """
    require_parent = True
    parent_classes = ['BootstrapColumnPlugin', 'ProcessStepPlugin', 'BootstrapPanelPlugin',
        'SegmentPlugin', 'SimpleWrapperPlugin', 'ValidateSetOfFormsPlugin']
    form = DialogPluginBaseForm

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
        render_type = dict(cls.form.RENDER_CHOICES).get(render_type, '')
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
