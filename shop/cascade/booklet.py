# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.forms import widgets
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from django.utils.text import Truncator
from django.utils.html import format_html
from django.forms.models import ModelForm
from django.forms.fields import IntegerField
from django.template.loader import select_template
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.forms import ManageChildrenFormMixin
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.widgets import NumberInputWidget
from cmsplugin_cascade.bootstrap3.buttons import ButtonSizeRenderer, ButtonTypeRenderer
from shop.cascade.plugin_base import ShopPluginBase
from shop import settings as shop_settings


class BookletForm(ManageChildrenFormMixin, ModelForm):
    num_children = IntegerField(min_value=1, initial=1,
        widget=NumberInputWidget(attrs={'size': '3', 'style': 'width: 5em;'}),
        label=_("Booklet"),
        help_text=_("Number of pages for this booklet."))


class DialogBookletPlugin(ShopPluginBase):
    name = _("Dialog Booklet")
    form = BookletForm
    default_css_class = 'btn-group btn-breadcrumb'
    parent_classes = ('BootstrapRowPlugin', 'BootstrapColumnPlugin',)
    require_parent = True
    allow_children = True
    fields = ('num_children', 'glossary',)

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(DialogBookletPlugin, cls).get_identifier(obj)
        num_cols = obj.get_children().count()
        content = ungettext_lazy('with {0} page', 'with {0} pages', num_cols).format(num_cols)
        return format_html('{0}{1}', identifier, content)

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/booklet.html'.format(shop_settings.APP_LABEL),
            'shop/booklet.html',
        ]
        return select_template(template_names)

    def save_model(self, request, obj, form, change):
        wanted_children = int(form.cleaned_data.get('num_children'))
        super(DialogBookletPlugin, self).save_model(request, obj, form, change)
        self.extend_children(obj, wanted_children, DialogPagePlugin)

plugin_pool.register_plugin(DialogBookletPlugin)


class BookletPageModelMixin(object):
    def slug(self):
        return self.glossary.get('slug', '')


class DialogPagePlugin(ShopPluginBase):
    name = _("Dialog Page")
    parent_classes = ('DialogBookletPlugin',)
    require_parent = True
    allow_children = True
    alien_child_classes = True
    model_mixins = (BookletPageModelMixin,)
    glossary_fields = (
        PartialFormField('page_title',
            widgets.TextInput(attrs={'size': 150}),
            label=_('Page Title')
        ),
        PartialFormField('slug',
            widgets.TextInput(attrs={'size': 150}),
            label=_('Slug')
        ),
    )

    class Media:
        js = ('admin/js/urlify.js', 'shop/js/admin/bookletplugin.js',)

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(DialogPagePlugin, cls).get_identifier(obj)
        content = obj.glossary.get('page_title', '')
        if content:
            content = unicode(Truncator(content).words(3, truncate=' ...'))
        return format_html('{0}{1}', identifier, content)

    def get_child_classes(self, slot, page):
        """
        Bypass allowed children from grandparent plugin.
        """
        instance = self.cms_plugin_instance
        if instance and instance.parent and instance.parent.parent:
            plugin_class = instance.parent.parent.get_plugin_class()
            child_classes = plugin_class().get_child_classes(slot, page)
        else:
            child_classes = super(DialogBookletPlugin, self).get_child_classes(slot, page)
        return child_classes

plugin_pool.register_plugin(DialogPagePlugin)


class BookletProceedButtonPlugin(ShopPluginBase):
    parent_classes = ('DialogPagePlugin',)
    require_parent = True
    render_template = 'cascade/bootstrap3/button.html'
    allow_children = False
    text_enabled = True
    tag_type = None
    default_css_class = 'btn'
    default_css_attributes = ('button-type', 'button-size', 'button-options', 'quick-float',)
    fields = ('link_content', ('link_type', 'cms_page', 'ext_url', 'mail_to'), 'glossary',)
    glossary_fields = (
        PartialFormField('button-type',
            widgets.RadioSelect(choices=((k, v) for k, v in ButtonTypeRenderer.BUTTON_TYPES.items()),
                                renderer=ButtonTypeRenderer),
            label=_('Button Type'),
            initial='btn-default',
            help_text=_("Display Link using this Button Style")
        ),
        PartialFormField('button-size',
            widgets.RadioSelect(choices=((k, v) for k, v in ButtonSizeRenderer.BUTTON_SIZES.items()),
                                renderer=ButtonSizeRenderer),
            label=_('Button Size'),
            initial='',
            help_text=_("Display Link using this Button Size")
        ),
        PartialFormField('button-options',
            widgets.CheckboxSelectMultiple(choices=(('btn-block', _('Block level')), ('disabled', _('Disabled')),)),
            label=_('Button Options'),
        ),
        PartialFormField('quick-float',
            widgets.RadioSelect(choices=(('', _("Do not float")), ('pull-left', _("Pull left")), ('pull-right', _("Pull right")),)),
            label=_('Quick Float'),
            initial='',
            help_text=_("Float the button to the left or right.")
        ),
    )

    class Media:
        css = {'all': ('cascade/css/admin/bootstrap.min.css', 'cascade/css/admin/bootstrap-theme.min.css',)}

plugin_pool.register_plugin(BookletProceedButtonPlugin)
