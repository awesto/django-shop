# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models import Max
from django.utils.translation import ugettext_lazy as _
from django.template.context import Context
from django.template.loader import get_template
from cms.models import Page
from cms.admin.placeholderadmin import PlaceholderAdminMixin, FrontendEditableAdminMixin
from parler.admin import TranslatableAdmin
from polymorphic.admin import PolymorphicChildModelAdmin
from reversion import VersionAdmin
from myshop.models.shopmodels import Product
from .image import ProductImageInline


class CommodityAdmin(TranslatableAdmin, VersionAdmin, FrontendEditableAdminMixin,
                     PlaceholderAdminMixin, PolymorphicChildModelAdmin):
    base_model = Product
    fieldsets = (
        (None, {
            'fields': ('identifier', ('unit_price', 'active',),)
        }),
        (_("Translatable Fields"), {
            'fields': ('name', 'slug', 'description',)
        }),
        (_("Properties"), {
            'fields': ('cms_pages',),
        }),
        (_("Render search indices"), {
            'fields': ('render_text_index',)
        }),
    )
    filter_horizontal = ('cms_pages',)
    inlines = (ProductImageInline,)
    readonly_fields = ('render_text_index',)

    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('name',)}

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'cms_pages':
            # restrict many-to-many field for cms_pages to ProductApp only
            limit_choices_to = {'publisher_is_draft': False, 'application_urls': 'CommodityListApp'}
            kwargs['queryset'] = Page.objects.filter(**limit_choices_to)
        return super(CommodityAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:
            # since SortableAdminMixin is missing on this class, ordering has to be computed by hand
            max_order = self.base_model.objects.aggregate(max_order=Max('order'))['max_order']
            obj.order = max_order + 1 if max_order else 1
        obj.legacy_fixed = True
        super(CommodityAdmin, self).save_model(request, obj, form, change)

    def render_text_index(self, instance):
        template = get_template('search/indexes/myshop/commodity_text.txt')
        return template.render(Context({'object': instance}))
    render_text_index.short_description = _("Text Index")
