from django.contrib.admin import StackedInline
from django.forms import fields, widgets
from django.forms.models import ModelForm
from django.template.loader import select_template
from django.utils.translation import ugettext_lazy as _, ugettext
from entangled.forms import EntangledModelFormMixin
from cms.plugin_pool import plugin_pool
from cms.utils.compat.dj import is_installed
from cmsplugin_cascade.mixins import WithSortableInlineElementsMixin
from cmsplugin_cascade.models import SortableInlineCascadeElement
from shop.cascade.plugin_base import ShopPluginBase, ProductSelectField
from shop.conf import app_settings
from shop.models.product import ProductModel

@plugin_pool.register_plugin
class ShopNavbarLoginLogout(ShopPluginBase):
    name = _("Nav Login-Logout")
    require_parent = True
#    form = ShopCatalogPluginForm
    parent_classes = ['BootstrapListsPlugin']
    cache = False
    render_template = 'shop/navbar/login-logout.html'


@plugin_pool.register_plugin
class ShopNavbarWatchList(ShopPluginBase):
    name = _("Nav WatchList")
    require_parent = True
    parent_classes = ['BootstrapListsPlugin']
    cache = False
    render_template = 'shop/navbar/watch-icon.html'


@plugin_pool.register_plugin
class ShopNavbarCart(ShopPluginBase):
    name = _("Nav Cart Caddy")
    require_parent = True
    parent_classes = ['BootstrapListsPlugin']
    cache = False
    render_template = 'shop/navbar/cart-caddy.html'


@plugin_pool.register_plugin
class ShopNavbarSearchForm(ShopPluginBase):
    name = _("Nav Search Form")
    require_parent = True
    parent_classes = ['BootstrapListsPlugin']
    cache = False
    render_template = 'shop/navbar/search-form.html'

