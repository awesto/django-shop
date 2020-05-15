from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.contrib import admin
from django.contrib.sites.models import Site
from django.utils.translation import gettext_lazy as _

try:
    from django_elasticsearch_dsl.registries import registry as elasticsearch_registry
except ImportError:
    elasticsearch_registry = type('DocumentRegistry', (), {'get_documents': lambda *args: []})()

from adminsortable2.admin import SortableInlineAdminMixin

from cms.models import Page

from shop.models.related import ProductPageModel, ProductImageModel


class ProductImageInline(SortableInlineAdminMixin, admin.StackedInline):
    model = ProductImageModel
    extra = 1
    ordering = ['order']


def _find_catalog_list_apphook():
    from shop.cms_apphooks import CatalogListCMSApp
    from cms.apphook_pool import apphook_pool

    for name, app in apphook_pool.apps.items():
        if isinstance(app, CatalogListCMSApp):
            return name
    else:
        raise ImproperlyConfigured("You must register a CMS apphook of type `CatalogListCMSApp`.")


class CategoryModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        if Site.objects.count() >=2 :
            page_sitename=str(Site.objects.filter(djangocms_nodes=obj.node_id).first().name)
            return '{} | {}'.format(str(obj), page_sitename)
        else:
            return str(obj)


class CMSPageAsCategoryMixin:
    """
    Add this mixin class to the ModelAdmin class for products wishing to be assigned to djangoCMS
    pages when used as categories.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not hasattr(self.model, 'cms_pages'):
            raise ImproperlyConfigured("Product model requires a field named `cms_pages`")

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(super().get_fieldsets(request, obj=obj))
        fieldsets.append((_("Categories"), {'fields': ('cms_pages',)}),)
        return fieldsets

    def get_fields(self, request, obj=None):
        # In ``get_fieldsets()``, ``cms_pages`` is added, so remove it from ``fields`` to
        # avoid showing it twice.
        fields = list(super().get_fields(request, obj))
        try:
            fields.remove('cms_pages')
        except ValueError:
            pass
        return fields

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'cms_pages':
            # restrict many-to-many field for cms_pages to ProductApp only
            limit_choices_to = {
                'publisher_is_draft': False,
                'application_urls': getattr(self, 'limit_to_cmsapp', _find_catalog_list_apphook()),
            }
            queryset = Page.objects.filter(**limit_choices_to)
            widget = admin.widgets.FilteredSelectMultiple(_("CMS Pages"), False)
            required = not db_field.blank
            field = CategoryModelMultipleChoiceField(queryset=queryset, widget=widget, required=required)
            return field
        return super().formfield_for_manytomany(db_field, request, **kwargs)

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

        return super().save_related(request, form, formsets, change)


class SearchProductIndexMixin:
    """
    If Elasticsearch is used to create a full text search index, add this mixin class to Django's
    ``ModelAdmin`` backend for the corresponding product model.
    """
    def save_model(self, request, product, form, change):
        super().save_model(request, product, form, change)
        if change:
            product.update_search_index()

    def delete_model(self, request, product):
        product.active = False
        product.update_search_index()
        super().delete_model(request, product)


class InvalidateProductCacheMixin:
    """
    If Redis caching is used to create a HTML snippets for product representation, add this mixin
    class to Django's ``ModelAdmin`` backend for the corresponding product model.
    """
    def save_model(self, request, product, form, change):
        if change:
            product.invalidate_cache()
        return super().save_model(request, product, form, change)

    def delete_model(self, request, product):
        product.invalidate_cache()
        super().delete_model(request, product)


class UnitPriceMixin:
    def get_list_display(self, request):
        list_display = list(super().get_list_display(request))
        list_display.append('get_unit_price')
        return list_display

    def get_unit_price(self, obj):
        return str(obj.unit_price)
    get_unit_price.short_description = _("Unit Price")


class CMSPageFilter(admin.SimpleListFilter):
    title = _("Category")
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        limit_choices_to = {
            'publisher_is_draft': False,
            'application_urls': getattr(self, 'limit_to_cmsapp', _find_catalog_list_apphook())
        }
        queryset = Page.objects.filter(**limit_choices_to)
        return [(page.id, page.get_title()) for page in queryset]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(cms_pages__id=self.value())
