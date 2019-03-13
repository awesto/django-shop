# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.admin import StackedInline
from django.forms import widgets
from django.forms.models import ModelForm
from django.template.loader import select_template
from django.utils.translation import ugettext_lazy as _, ugettext
from cms.plugin_pool import plugin_pool
from cms.utils.compat.dj import is_installed
from cmsplugin_cascade.mixins import WithSortableInlineElementsMixin
from cmsplugin_cascade.models import SortableInlineCascadeElement
from cmsplugin_cascade.fields import GlossaryField
from shop.cascade.plugin_base import ShopPluginBase, ProductSelectField
from shop.conf import app_settings
from shop.models.product import ProductModel

if is_installed('adminsortable2'):
    from adminsortable2.admin import SortableInlineAdminMixin
else:
    SortableInlineAdminMixin = type(str('SortableInlineAdminMixin'), (object,), {})


class ShopCatalogPlugin(ShopPluginBase):
    name = _("Catalog List View")
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin', 'SimpleWrapperPlugin',)
    cache = False

    pagination = GlossaryField(
        widgets.RadioSelect(choices=[
            ('paginator', _("Use Paginator")), ('manual', _("Manual Infinite")), ('auto', _("Auto Infinite"))
        ]),
        label=_("Pagination"),
        initial=True,
        help_text=_("Shall the product list view use a paginator or scroll infinitely?"),
    )

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
            return ugettext("Manual Pagination")
        return ugettext("Infinite Scroll")

plugin_pool.register_plugin(ShopCatalogPlugin)


class ShopAddToCartPlugin(ShopPluginBase):
    name = _("Add Product to Cart")
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin',)
    cache = False

    use_modal_dialog = GlossaryField(
        widgets.CheckboxInput(),
        label=_("Use Modal Dialog"),
        initial='on',
        help_text=_("After adding product to cart, render a modal dialog"),
    )

    def get_render_template(self, context, instance, placeholder):
        templates = []
        if instance.glossary.get('render_template'):
            templates.append(instance.glossary['render_template'])
        templates.extend([
            '{}/catalog/product-add2cart.html'.format(app_settings.APP_LABEL),
            'shop/catalog/product-add2cart.html',
        ])
        return select_template(templates)

    def render(self, context, instance, placeholder):
        context = super(ShopAddToCartPlugin, self).render(context, instance, placeholder)
        context['use_modal_dialog'] = bool(instance.glossary.get('use_modal_dialog', True))
        return context

plugin_pool.register_plugin(ShopAddToCartPlugin)


class ProductGalleryForm(ModelForm):
    product = ProductSelectField(
        required=False,
        label=_("Related Product"),
        help_text=_("Choose related product"),
    )

    class Meta:
        exclude = ('glossary',)

    def __init__(self, *args, **kwargs):
        try:
            initial = dict(kwargs['instance'].glossary)
        except (KeyError, AttributeError):
            initial = {}
        initial.update(kwargs.pop('initial', {}))
        try:
            self.base_fields['product'].initial = initial['product']['pk']
        except KeyError:
            self.base_fields['product'].initial = None
        if not is_installed('adminsortable2'):
            self.base_fields['order'].widget = widgets.HiddenInput()
            self.base_fields['order'].initial = 0
        super(ProductGalleryForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(ProductGalleryForm, self).clean()
        if self.is_valid():
            product_pk = self.cleaned_data.pop('product', None)
            if product_pk:
                product_data = {'pk': product_pk}
                self.instance.glossary.update(product=product_data)
            else:
                self.instance.glossary.pop('image', None)
        return cleaned_data


class ProductGalleryInline(SortableInlineAdminMixin, StackedInline):
    model = SortableInlineCascadeElement
    raw_id_fields = ('product',)
    form = ProductGalleryForm
    extra = 5
    ordering = ('order',)
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
            except KeyError:
                pass
        queryset = ProductModel.objects.filter(pk__in=product_ids, active=True)
        serializer_class = app_settings.PRODUCT_SUMMARY_SERIALIZER
        serialized = serializer_class(queryset, many=True, context={'request': context['request']})
        # sort the products according to the order provided by `sortinline_elements`.
        context['products'] = [product for id in product_ids for product in serialized.data if product['id'] == id]
        return context

plugin_pool.register_plugin(ShopProductGallery)
