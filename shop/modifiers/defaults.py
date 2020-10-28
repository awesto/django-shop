from decimal import Decimal
from django.utils.translation import gettext_lazy as _
from shop import messages
from shop.exceptions import ProductNotAvailable
from shop.money import AbstractMoney, Money
from shop.modifiers.base import BaseCartModifier


class DefaultCartModifier(BaseCartModifier):
    """
    This modifier is required for almost every shopping cart. It handles the most basic
    calculations, ie. multiplying the items unit prices with the chosen quantity.
    Since this modifier sets the cart items line total, it must be listed as the first
    entry in `SHOP_CART_MODIFIERS`.
    """
    identifier = 'default'

    def pre_process_cart_item(self, cart, cart_item, request, raise_exception=False):
        """
        Limit the ordered quantity in the cart to the availability in the inventory.
        """
        kwargs = {'product_code': cart_item.product_code}
        kwargs.update(cart_item.extra)
        availability = cart_item.product.get_availability(request, **kwargs)
        if cart_item.quantity > availability.quantity:
            if raise_exception:
                raise ProductNotAvailable(cart_item.product)
            cart_item.quantity = availability.quantity
            cart_item.save(update_fields=['quantity'])
            message = _("The ordered quantity for item '{product_name}' has been adjusted to "\
                        "{quantity} which is the maximum, currently available in stock.").\
                        format(product_name=cart_item.product.product_name, quantity=availability.quantity)
            messages.info(request, message, title=_("Verify Quantity"), delay=5)
        return super().pre_process_cart_item(cart, cart_item, request, raise_exception)

    def process_cart_item(self, cart_item, request):
        cart_item.unit_price = cart_item.product.get_price(request)
        cart_item.line_total = cart_item.unit_price * cart_item.quantity
        return super().process_cart_item(cart_item, request)

    def process_cart(self, cart, request):
        if not isinstance(cart.subtotal, AbstractMoney):
            # if we don't know the currency, use the default
            cart.subtotal = Money(cart.subtotal)
        cart.total = cart.subtotal
        return super().process_cart(cart, request)


class WeightedCartModifier(BaseCartModifier):
    """
    This modifier is required for all shopping cart where we are interested into its weight.
    It sums up the weight of all articles, ie. multiplying the items weight with the chosen
    quantity.
    If this modifier is used, the classes implementing the product shall override their
    method ``get_weight()``, which must return the weight in kg as Decimal type.
    """
    identifier = 'weights'
    initial_weight = Decimal(0.01)  # in kg

    def pre_process_cart(self, cart, request, raise_exception=False):
        cart.weight = self.initial_weight
        return super().pre_process_cart(cart, request, raise_exception)

    def pre_process_cart_item(self, cart, cart_item, request, raise_exception=False):
        cart.weight += Decimal(cart_item.product.get_weight() * cart_item.quantity)
        return super().pre_process_cart_item(cart_item, request, raise_exception)
