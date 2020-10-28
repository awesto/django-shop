from django.conf import settings
from django.utils.translation import gettext_lazy as _
from cmsplugin_cascade.bootstrap4.mixins import BootstrapUtilities


CASCADE_PLUGINS = getattr(settings, 'SHOP_CASCADE_PLUGINS',
    ['auth', 'breadcrumb', 'catalog', 'cart', 'checkout', 'extensions', 'order', 'processbar', 'search']
)


def set_defaults(config):
    config.setdefault('plugins_with_extra_mixins', {})
    config.setdefault('plugins_with_extra_render_templates', {})
    config['plugins_with_extra_mixins'].setdefault('ShopReorderButtonPlugin', BootstrapUtilities(
        BootstrapUtilities.margins, BootstrapUtilities.floats,
    ))
    config['plugins_with_extra_mixins'].setdefault('ShopCancelOrderButtonPlugin', BootstrapUtilities(
        BootstrapUtilities.margins, BootstrapUtilities.floats,
    ))
    config['plugins_with_extra_mixins'].setdefault('ShopProceedButton', BootstrapUtilities(
        BootstrapUtilities.margins, BootstrapUtilities.floats,
    ))
    config['plugins_with_extra_mixins'].setdefault('ShopLeftExtension', BootstrapUtilities(
        BootstrapUtilities.paddings,
    ))
    config['plugins_with_extra_mixins'].setdefault('ShopRightExtension', BootstrapUtilities(
        BootstrapUtilities.paddings,
    ))
    config['plugins_with_extra_mixins'].setdefault('ShopAddToCartPlugin', BootstrapUtilities(
        BootstrapUtilities.margins,
    ))
    config['plugins_with_extra_mixins'].setdefault('BootstrapButtonPlugin', BootstrapUtilities(
        BootstrapUtilities.floats,
    ))
    config['plugins_with_extra_render_templates'].setdefault('BootstrapButtonPlugin', [
        ('shop/button.html', _("Responsive Feedback")),
        ('cascade/bootstrap4/button.html', _("Default")),
    ])
