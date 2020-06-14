from django.forms import fields, widgets
from django.template import engines, TemplateDoesNotExist
from django.template.loader import select_template, get_template
from django.utils.translation import gettext_lazy as _
from django.utils.html import mark_safe
from entangled.forms import EntangledModelFormMixin
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.plugin_base import TransparentWrapper
from shop.cascade.extensions import ShopExtendableMixin, LeftRightExtensionMixin
from shop.cascade.plugin_base import ShopPluginBase
from shop.conf import app_settings
from shop.models.cart import CartModel
from shop.serializers.cart import CartSerializer


class ShopCartPluginForm(EntangledModelFormMixin):
    CHOICES = [
        ('editable', _("Editable Cart")),
        ('static', _("Static Cart")),
        ('summary', _("Cart Summary")),
        ('watch', _("Watch List")),
    ]

    render_type = fields.ChoiceField(
        choices=CHOICES,
        widget=widgets.RadioSelect,
        label=_("Render as"),
        initial='editable',
        help_text=_("Shall the cart be editable or a static summary?"),
    )

    class Meta:
        entangled_fields = {'glossary': ['render_type']}


class ShopCartPlugin(LeftRightExtensionMixin, TransparentWrapper, ShopPluginBase):
    name = _("Shopping Cart")
    require_parent = True
    parent_classes = ['BootstrapColumnPlugin']
    cache = False
    allow_children = True
    form = ShopCartPluginForm
    model_mixins = (ShopExtendableMixin,)

    @classmethod
    def get_identifier(cls, instance):
        render_type = instance.glossary.get('render_type')
        return mark_safe(dict(cls.form.CHOICES).get(render_type, ''))

    def get_render_template(self, context, instance, placeholder):
        render_template = instance.glossary.get('render_template')
        if render_template:
            return get_template(render_template)
        render_type = instance.glossary.get('render_type')
        try:
            return select_template([
                '{}/cart/{}.html'.format(app_settings.APP_LABEL, render_type),
                'shop/cart/{}.html'.format(render_type),
            ])
        except TemplateDoesNotExist:
            return get_template('shop/cart/editable.html')

    def render(self, context, instance, placeholder):
        try:
            cart = CartModel.objects.get_from_request(context['request'])
            context['is_cart_filled'] = cart.items.exists()
            render_type = instance.glossary['render_type']
            if render_type == 'static':
                # update context for static cart with items to be endered as HTML
                cart_serializer = CartSerializer(cart, context=context, label='cart', with_items=True)
                context['cart'] = cart_serializer.data
            elif render_type == 'summary':
                # update context for cart summary to be endered as HTML
                cart_serializer = CartSerializer(cart, context=context, label='cart')
                context['cart'] = cart_serializer.data
        except (KeyError, CartModel.DoesNotExist):
            pass
        return self.super(ShopCartPlugin, self).render(context, instance, placeholder)

plugin_pool.register_plugin(ShopCartPlugin)
