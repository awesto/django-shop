# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from django.db.models import Max
from django.utils.translation import ugettext_lazy as _
from django.template.context import Context
from django.template.loader import get_template
from cms.models import Page
from cms.admin.placeholderadmin import PlaceholderAdminMixin, FrontendEditableAdminMixin
from parler.admin import TranslatableAdmin
from polymorphic.admin import PolymorphicChildModelAdmin
from reversion import VersionAdmin
from myshop.models.product import Product
from myshop.models.smartphone import SmartPhone, Manufacturer, OperatingSystem
from .image import ProductImageInline


class ManufacturerAdmin(admin.ModelAdmin):
    pass

admin.site.register(Manufacturer, ManufacturerAdmin)


class OperatingSystemAdmin(admin.ModelAdmin):
    pass

admin.site.register(OperatingSystem, OperatingSystemAdmin)


class SmartPhoneInline(admin.TabularInline):
    model = SmartPhone
    extra = 0


class SmartPhoneAdmin(TranslatableAdmin, VersionAdmin, FrontendEditableAdminMixin,
                      PlaceholderAdminMixin, PolymorphicChildModelAdmin):
    base_model = Product
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'active',),
        }),
        (_("Translatable Fields"), {
            'fields': ('description',)
        }),
        (_("Categories"), {
            'fields': ('cms_pages',),
        }),
        (_("Properties"), {
            'fields': ('manufacturer', 'battery_type', 'battery_capacity', 'ram_storage',
                'wifi_connectivity', 'bluetooth', 'gps', 'operating_system',
                ('width', 'height', 'weight',), 'screen_size'),
        }),
    )
    filter_horizontal = ('cms_pages',)
    inlines = (ProductImageInline, SmartPhoneInline,)
    prepopulated_fields = {'slug': ('name',)}

#    def get_prepopulated_fields(self, request, obj=None):
#        return {'slug': ('name',)}

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'cms_pages':
            # restrict many-to-many field for cms_pages to ProductApp only
            limit_choices_to = {'publisher_is_draft': False, 'application_urls': 'ProductsListApp'}
            kwargs['queryset'] = Page.objects.filter(**limit_choices_to)
        return super(SmartPhoneAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:
            # since SortableAdminMixin is missing on this class, ordering has to be computed by hand
            max_order = self.base_model.objects.aggregate(max_order=Max('order'))['max_order']
            obj.order = max_order + 1 if max_order else 1
        obj.legacy_fixed = True
        super(SmartPhoneAdmin, self).save_model(request, obj, form, change)

    def render_text_index(self, instance):
        template = get_template('search/indexes/myshop/commodity_text.txt')
        return template.render(Context({'object': instance}))
    render_text_index.short_description = _("Text Index")
