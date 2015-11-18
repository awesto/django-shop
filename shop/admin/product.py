# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import warnings
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _
from cms.models import Page
from myshop.models.product import ProductPage
from django.core.exceptions import ImproperlyConfigured


class InvalidateProductCacheMixin(object):
    def __init__(self, *args, **kwargs):
        if not hasattr(cache, 'delete_pattern'):
            warnings.warn("Your caching backend does not support deletion by key patterns. "
                "Please use `django-redis-cache`, or wait until the product's HTML snippet cache "
                "expires by itself")
        super(InvalidateProductCacheMixin, self).__init__(*args, **kwargs)

    def save_model(self, request, product, form, change):
        if change:
            self.invalidate_cache(product)
        super(InvalidateProductCacheMixin, self).save_model(request, product, form, change)

    def invalidate_cache(self, product):
        """
        The method ``ProductCommonSerializer.render_html`` caches the rendered HTML snippets.
        Invalidate them after changing something in the product.
        """
        try:
            cache.delete_pattern('product:{}|*'.format(product.id))
        except AttributeError:
            pass


class CMSPageAsCategoryMixin(object):
    """
    Add this mixin class to the ModelAdmin class for products wishing to be assigned to djangoCMS
    pages when used as categories.
    """
    def __init__(self, *args, **kwargs):
        super(CMSPageAsCategoryMixin, self).__init__(*args, **kwargs)
        if not hasattr(self.model, 'cms_pages'):
            raise ImproperlyConfigured("Product model requires a field named `cms_pages`")

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'cms_pages':
            # restrict many-to-many field for cms_pages to ProductApp only
            limit_choices_to = {'publisher_is_draft': False, 'application_urls': 'ProductsListApp'}
            queryset = Page.objects.filter(**limit_choices_to)
            widget = FilteredSelectMultiple(_("CMS Pages"), False)
            field = forms.ModelMultipleChoiceField(queryset=queryset, widget=widget)
            return field
        return super(CMSPageAsCategoryMixin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def save_related(self, request, form, formsets, change):
        cms_pages = form.cleaned_data.pop('cms_pages')
        # remove old
        for page in form.instance.cms_pages.all():
            if page not in cms_pages:
                try:
                    ProductPage.objects.get(product=form.instance, page=page).delete()
                except ProductPage.DoesNotExist:
                    pass

        # add new
        for page in cms_pages.all():
            ProductPage.objects.create(product=form.instance, page=page)

        return super(CMSPageAsCategoryMixin, self).save_related(request, form, formsets, change)
