from django.utils.translation import ugettext_lazy as _, ugettext
from entangled.forms import EntangledModelFormMixin
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.mixins import WithSortableInlineElementsMixin
from shop.cascade.plugin_base import ShopPluginBase
from django.utils.html import format_html

@plugin_pool.register_plugin
class ShopNavbarLoginLogout(ShopPluginBase):
    name = _("Nav Login-Logout")
    require_parent = True
    parent_classes = ['BootstrapListsPlugin']
    cache = False
    render_template = 'shop/navbar/login-logout.html'

    @classmethod
    def get_identifier(cls, obj):
        identifier = super().get_identifier(obj)
        if hasattr(cls,'default_css_class'):
            css_classes_without_default = obj.css_classes.replace( cls.default_css_class , '' , 1)
        else:
            css_classes_without_default = obj.css_classes
        return format_html('<div style="font-size: smaller; white-space: pre-wrap;" >{0}{1}</div>',
        identifier, css_classes_without_default )

@plugin_pool.register_plugin
class ShopNavbarWatchList(ShopPluginBase):
    name = _("Nav WatchList")
    require_parent = True
    parent_classes = ['BootstrapListsPlugin']
    cache = False
    render_template = 'shop/navbar/watch-icon.html'

    @classmethod
    def get_identifier(cls, obj):
        identifier = super().get_identifier(obj)
        if hasattr(cls,'default_css_class'):
            css_classes_without_default = obj.css_classes.replace( cls.default_css_class , '' , 1)
        else:
            css_classes_without_default = obj.css_classes
        return format_html('<div style="font-size: smaller; white-space: pre-wrap;" >{0}{1}</div>',
        identifier, css_classes_without_default )


@plugin_pool.register_plugin
class ShopNavbarCart(ShopPluginBase):
    name = _("Nav Cart Caddy")
    require_parent = True
    parent_classes = ['BootstrapListsPlugin']
    cache = False
    render_template = 'shop/navbar/cart-caddy.html'

    @classmethod
    def get_identifier(cls, obj):
        identifier = super().get_identifier(obj)
        if hasattr(cls,'default_css_class'):
            css_classes_without_default = obj.css_classes.replace( cls.default_css_class , '' , 1)
        else:
            css_classes_without_default = obj.css_classes
        return format_html('<div style="font-size: smaller; white-space: pre-wrap;" >{0}{1}</div>',
        identifier, css_classes_without_default )


@plugin_pool.register_plugin
class ShopNavbarSearchForm(ShopPluginBase):
    name = _("Nav Search Form")
    require_parent = True
    parent_classes = ['BootstrapListsPlugin']
    cache = False
    render_template = 'shop/navbar/search-form.html'


    @classmethod
    def get_identifier(cls, obj):
        identifier = super().get_identifier(obj)
        if hasattr(cls,'default_css_class'):
            css_classes_without_default = obj.css_classes.replace( cls.default_css_class , '' , 1)
        else:
            css_classes_without_default = obj.css_classes
        return format_html('<div style="font-size: smaller; white-space: pre-wrap;" >{0}{1}</div>',
        identifier, css_classes_without_default )
