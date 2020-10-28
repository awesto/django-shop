from django.contrib.admin import StackedInline
from django.forms import fields, widgets
from django.template.loader import select_template
from django.utils.translation import gettext_lazy as _, gettext

from entangled.forms import EntangledModelFormMixin, EntangledModelForm

from cms.plugin_pool import plugin_pool
from cms.utils.compat.dj import is_installed
from cmsplugin_cascade.mixins import WithSortableInlineElementsMixin
from cmsplugin_cascade.models import SortableInlineCascadeElement

from shop.cascade.plugin_base import ShopPluginBase, ProductSelectField
from shop.conf import app_settings
from shop.models.product import ProductModel

if is_installed('adminsortable2'):
    from adminsortable2.admin import SortableInlineAdminMixin
else:
    SortableInlineAdminMixin = type('SortableInlineAdminMixin', (object,), {})


class ShopCatalogPluginForm(EntangledModelFormMixin):
    CHOICES = [
        ('paginator', _("Use Paginator")),
        ('manual', _("Manual Infinite")),
        ('auto', _("Auto Infinite")),
    ]

    pagination = fields.ChoiceField(
        choices=CHOICES,
        widget=widgets.RadioSelect,
        label=_("Pagination"),
        initial='paginator',
        help_text=_("Shall the product list view use a paginator or scroll infinitely?"),
    )

    class Meta:
        entangled_fields = {'glossary': ['pagination']}


class ShopCatalogPlugin(ShopPluginBase):
    name = _("Catalog List View")
    require_parent = True
    form = ShopCatalogPluginForm
    parent_classes = ['BootstrapColumnPlugin', 'SimpleWrapperPlugin']
    cache = False

    def get_render_template(self, context, instance, placeholder):
        templates = []
        if instance.glossary.get('render_template'):
            templates.append(instance.glossary['render_template'])
        templates.extend([
            '{}/catalog/list.html'.format(app_settings.APP_LABEL),
            'shop/catalog/list.html',
        ])
        return select_template(templates)

    def render(self, context, instance, placeholder):
        context['pagination'] = instance.glossary.get('pagination', 'paginator')
        return context

    @classmethod
    def get_identifier(cls, obj):
        pagination = obj.glossary.get('pagination')
        if pagination == 'paginator':
            return gettext("Manual Pagination")
        return gettext("Infinite Scroll")

plugin_pool.register_plugin(ShopCatalogPlugin)


class ShopAddToCartPluginForm(EntangledModelFormMixin):
    use_modal_dialog = fields.BooleanField(
        label=_("Use Modal Dialog"),
        initial=True,
        required=False,
        help_text=_("After adding product to cart, render a modal dialog"),
    )

    class Meta:
        entangled_fields = {'glossary': ['use_modal_dialog']}


class ShopAddToCartPlugin(ShopPluginBase):
    name = _("Add Product to Cart")
    require_parent = True
    form = ShopAddToCartPluginForm
    parent_classes = ['BootstrapColumnPlugin']
    cache = False

    def get_render_template(self, context, instance, placeholder):
        templates = []
        if instance.glossary.get('render_template'):
            templates.append(instance.glossary['render_template'])
        if context['product'].managed_availability():
            template_prefix = 'available-'
        else:
            template_prefix = ''
        templates.extend([
            '{}/catalog/{}product-add2cart.html'.format(app_settings.APP_LABEL, template_prefix),
            'shop/catalog/{}product-add2cart.html'.format(template_prefix),
        ])
        return select_template(templates)

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        context['use_modal_dialog'] = bool(instance.glossary.get('use_modal_dialog', True))
        return context

plugin_pool.register_plugin(ShopAddToCartPlugin)


class ProductGalleryForm(EntangledModelForm):
    order = fields.IntegerField(
        widget=widgets.HiddenInput,
        initial=0,
    )

    product = ProductSelectField(
        required=False,
        label=_("Related Product"),
        help_text=_("Choose related product"),
    )

    class Meta:
        entangled_fields = {'glossary': ['product']}
        untangled_fields = ['order']


class ProductGalleryInline(SortableInlineAdminMixin, StackedInline):
    model = SortableInlineCascadeElement
    form = ProductGalleryForm
    extra = 5
    ordering = ['order']
    verbose_name = _("Product")
    verbose_name_plural = _("Product Gallery")


class ShopProductGallery(WithSortableInlineElementsMixin, ShopPluginBase):
    name = _("Product Gallery")
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin',)
    inlines = (ProductGalleryInline,)
    # until this bug https://github.com/applegrew/django-select2/issues/65 is fixed
    # we hide the a "add row" button and instead use `extra = 5` in ProductGalleryInline

    class Media:
        css = {'all': ('shop/css/admin/product-gallery.css',)}

    def get_render_template(self, context, instance, placeholder):
        templates = []
        if instance.glossary.get('render_template'):
            templates.append(instance.glossary['render_template'])
        templates.extend([
            '{}/catalog/product-gallery.html'.format(app_settings.APP_LABEL),
            'shop/catalog/product-gallery.html',
        ])
        return select_template(templates)

    def render(self, context, instance, placeholder):
        product_ids = []
        for inline in instance.sortinline_elements.all():
            try:
                product_ids.append(inline.glossary['product']['pk'])
            except TypeError:
                pass
        queryset = ProductModel.objects.filter(pk__in=product_ids, active=True)
        serializer_class = app_settings.PRODUCT_SUMMARY_SERIALIZER
        serialized = serializer_class(queryset, many=True, context={'request': context['request']})
        # sort the products according to the order provided by `sortinline_elements`.
        context['products'] = [product for id in product_ids for product in serialized.data if product['id'] == id]
        return context

plugin_pool.register_plugin(ShopProductGallery)
