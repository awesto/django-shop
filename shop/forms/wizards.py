from django.conf import settings
from django.db.models import Max
from django.forms import models, fields, widgets
from django.utils.translation import gettext_lazy as _
from cms.wizards.forms import BaseFormMixin
from djangocms_text_ckeditor.fields import HTMLFormField
from shop.models.related import ProductPageModel
from shop.models.defaults.commodity import Commodity


class CommodityWizardForm(BaseFormMixin, models.ModelForm):
    product_name = fields.CharField(label=_("Product Name"),
                                    widget=widgets.TextInput(attrs={'size': 50}))
    slug = fields.CharField(label=_("Slug"), widget=widgets.TextInput(attrs={'size': 50}))
    caption = HTMLFormField(label=_("Caption"), required=False)

    class Meta:
        model = Commodity
        fields = ('product_name', 'slug', 'caption', 'product_code',
                  'unit_price', 'active', 'show_breadcrumb', 'sample_image',)

    @property
    def media(self):
        minimized = '' if settings.DEBUG else '.min'
        media = super().media
        css = {'all': ['admin/css/base.css', 'admin/css/forms.css']}
        media.add_css(css)
        media._js = [
            'admin/js/core.js',
            'admin/js/vendor/jquery/jquery{}.js'.format(minimized),
            'admin/js/jquery.init.js',
            'admin/js/urlify.js',
            'admin/js/prepopulate{}.js'.format(minimized),
        ] + media._js
        media.add_js([
            'filer/js/libs/mediator.min.js',
            'filer/js/libs/jquery.cookie.min.js',
            'filer/js/libs/fileuploader.min.js',
            'admin/js/admin/RelatedObjectLookups.js',
        ])
        return media

    def save(self, commit=True):
        self.instance.product_name = self.cleaned_data['product_name']
        self.instance.caption = self.cleaned_data['caption']
        self.instance.slug = self.cleaned_data['slug']
        max_order = Commodity.objects.aggregate(max=Max('order'))['max']
        self.instance.order = max_order + 1 if max_order else 1
        commodity = super().save(commit)
        ProductPageModel.objects.create(product=commodity, page=self.page.get_public_object())
        return commodity
