# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.db.models import get_model
from django.core.exceptions import ObjectDoesNotExist
from django.forms import widgets
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.link.forms import TextLinkForm
from cmsplugin_cascade.link.fields import LinkSearchField
from cmsplugin_cascade.link.plugin_base import LinkPluginBase, LinkElementMixin
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.utils import resolve_dependencies
from shop.models.product import BaseProduct


class TextLinkFormBase(TextLinkForm):
    """
    Alternative implementation of ``cmsplugin_cascade.TextLinkForm``, which allows to link onto
    the Product model, using its method ``get_absolute_url``.

    Note: In this form class the field ``product`` is missing. It is added later, when the shop's
    Product knows about its MaterializedModel.
    """
    LINK_TYPE_CHOICES = (('cmspage', _("CMS Page")), ('product', _("Product")),
                         ('exturl', _("External URL")), ('email', _("Mail To")),)

    def clean_product(self):
        if self.cleaned_data.get('link_type') == 'product':
            app_label = self.ProductModel._meta.app_label
            self.cleaned_data['link_data'] = {
                'type': 'product',
                'model': '{0}.{1}'.format(app_label, self.ProductModel.__name__),
                'pk': self.cleaned_data['product'] and self.cleaned_data['product'].pk or None,
            }

    def set_initial_product(self, initial):
        try:
            Model = get_model(*initial['link']['model'].split('.'))
            initial['product'] = Model.objects.get(pk=initial['link']['pk'])
        except (KeyError, ObjectDoesNotExist):
            pass


class TextLinkPlugin(LinkPluginBase):
    """
    Modified implementation of ``cmsplugin_cascade.TextLinkPlugin`` which adds link type "Product",
    to set links onto arbitrary products of this shop.
    """
    name = _("Link")
    model_mixins = (LinkElementMixin,)
    render_template = 'cascade/plugins/link.html'
    glossary_fields = (
        PartialFormField('title',
            widgets.TextInput(),
            label=_("Title"),
            help_text=_("Link's Title")
        ),
    ) + LinkPluginBase.glossary_fields
    html_tag_attributes = dict(title='title', **LinkPluginBase.html_tag_attributes)
    fields = ('link_content', ('link_type', 'cms_page', 'product', 'ext_url', 'mail_to'), 'glossary',)
    glossary_field_map = {'link': ('link_type', 'cms_page', 'product', 'ext_url', 'mail_to',)}

    class Media:
        js = resolve_dependencies('shop/js/admin/shoplinkplugin.js')

    def get_form(self, request, obj=None, **kwargs):
        ProductModel = getattr(BaseProduct, 'MaterializedModel')
        # must add field `product` on the fly, because during the declaration of TextLinkFormBase
        # the MaterializedModel of the product is not known yet.
        product_field = LinkSearchField(required=False, label='',
            queryset=ProductModel.objects.all(),
            search_fields=getattr(ProductModel, 'search_fields'),
            help_text=_("An internal link onto a product from the shop"))
        Form = type('TextLinkForm', (TextLinkFormBase,), {'ProductModel': ProductModel, 'product': product_field})
        kwargs.update(form=Form)
        return super(TextLinkPlugin, self).get_form(request, obj, **kwargs)

plugin_pool.register_plugin(TextLinkPlugin)
