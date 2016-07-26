# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.forms import models
from cms.wizards.forms import BaseFormMixin
from shop.models.related import ProductPageModel
from shop.models.defaults.commodity import Commodity


class CommodityWizardForm(BaseFormMixin, models.ModelForm):
    class Meta:
        model = Commodity
        fields = ('product_name', 'slug', 'caption', 'product_code',
                  'unit_price', 'active', 'show_breadcrumb', 'sample_image',)

    @property
    def media(self):
        minimized = '' if settings.DEBUG else '.min'
        media = super(CommodityWizardForm, self).media
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
        commodity = super(CommodityWizardForm, self).save(commit)
        ProductPageModel.objects.create(product=commodity, page=self.page.get_public_object())
        return commodity
