# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import warnings
from django import forms
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from adminsortable2.admin import SortableInlineAdminMixin
from cms.models import Page
from shop.models.related import ProductPageModel, ProductImageModel


class ProductImageInline(SortableInlineAdminMixin, admin.StackedInline):
    model = ProductImageModel
    extra = 1
    ordering = ('order',)


class CMSPageAsCategoryMixin(object):
    """
    Add this mixin class to the ModelAdmin class for products wishing to be assigned to djangoCMS
    pages when used as categories.
    """
    def __init__(self, *args, **kwargs):
        super(CMSPageAsCategoryMixin, self).__init__(*args, **kwargs)
        if not hasattr(self.model, 'cms_pages'):
            raise ImproperlyConfigured("Product model requires a field named `cms_pages`")

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(super(CMSPageAsCategoryMixin, self).get_fieldsets(request, obj=obj))
        fieldsets.append((_("Categories"), {'fields': ('cms_pages',)}),)
        return fieldsets

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'cms_pages':
            # restrict many-to-many field for cms_pages to ProductApp only
            limit_choices_to = {'publisher_is_draft': False, 'application_urls': 'ProductsListApp'}
            queryset = Page.objects.filter(**limit_choices_to)
            widget = admin.widgets.FilteredSelectMultiple(_("CMS Pages"), False)
            field = forms.ModelMultipleChoiceField(queryset=queryset, widget=widget)
            return field
        return super(CMSPageAsCategoryMixin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def save_related(self, request, form, formsets, change):
        old_cms_pages = form.instance.cms_pages.all()
        new_cms_pages = form.cleaned_data.pop('cms_pages')

        # remove old
        for page in old_cms_pages:
            if page not in new_cms_pages:
                for pp in ProductPageModel.objects.filter(product=form.instance, page=page):
                    pp.delete()

        # add new
        for page in new_cms_pages:
            if page not in old_cms_pages:
                ProductPageModel.objects.create(product=form.instance, page=page)

        return super(CMSPageAsCategoryMixin, self).save_related(request, form, formsets, change)


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
