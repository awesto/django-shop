from django.core import checks
from django.db import models
from django.db.models.aggregates import Sum
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from shop.conf import app_settings
from shop.models.product import Availability, BaseReserveProductMixin
from shop.exceptions import ProductNotAvailable


class AvailableProductMixin:
    """
    Add this mixin class to the product models declaration, wanting to keep track on the
    current amount of products in stock. In comparison to
    :class:`shop.models.product.ReserveProductMixin`, this mixin does not reserve items in pending
    carts, with the risk for overselling. It thus is suited for products kept in the cart
    for a long period.

    The product class must implement a field named ``quantity`` accepting numerical values.
    """
    def get_availability(self, request, **kwargs):
        """
        Returns the current available quantity for this product.

        If other customers have pending carts containing this same product, the quantity
        is not not adjusted. This may result in a situation, where someone adds a product
        to the cart, but then is unable to purchase, because someone else bought it in the
        meantime.
        is not adjusted. This may result in a situation, where someone adds a product to the cart,
        but then is unable to purchase, because someone else bought it in the meantime.
        """
        def create_availability(**kwargs):
            quantity = inventory_set.aggregate(sum=Sum('quantity'))['sum']
            inventory = inventory_set.order_by('earliest').first()
            earliest = inventory.earliest
            latest = inventory_set.order_by('latest').last().latest
            if latest < now + app_settings.SHOP_LIMITED_OFFER_PERIOD:
                kwargs['limited_offer'] = True
            return Availability(quantity=quantity, earliest=earliest, latest=latest, **kwargs)

        now = timezone.now()
        inventory_set = self.inventory_set.filter(earliest__lt=now, latest__gt=now, quantity__gt=0)
        if inventory_set.exists():
            return create_availability()
        # check, if we can sell short
        later = now + app_settings.SHOP_SELL_SHORT_PERIOD
        inventory_set = self.inventory_set.filter(earliest__lt=later, latest__gt=now, quantity__gt=0)
        if inventory_set.exists():
            return create_availability(sell_short=True)
        return Availability(quantity=0)

    def deduct_from_stock(self, quantity, **kwargs):
        """
        Deduce requested quantity from all available inventories.
        """
        later = timezone.now() + app_settings.SHOP_SELL_SHORT_PERIOD
        for inventory in self.inventory_set.filter(earliest__lt=later, quantity__gt=0).order_by('earliest', 'latest'):
            reduce_by = min(inventory.quantity, quantity)
            inventory.quantity -= reduce_by
            inventory.save(update_fields=['quantity'])
            quantity -= reduce_by
            if quantity == 0:
                break
        else:
            raise ProductNotAvailable(self)

    def managed_availability(self):
        return True

    @classmethod
    def check(cls, **kwargs):
        errors = super().check(**kwargs)
        for rel in cls._meta.related_objects:
            if rel.name == 'inventory_set':
                if rel.get_internal_type() != 'ForeignKey':
                    msg = "Field `product` in class inheriting from `BaseInventory` is not a valid foreign key pointing onto {}."
                    errors.append(checks.Error(msg.format(cls.__name__)))
                break
        else:
            msg = "A model inheriting from `BaseInventory` must implement a foreign key `product` pointing onto {}."
            errors.append(checks.Error(msg.format(cls.__name__)))
        return errors


class ReserveProductMixin(BaseReserveProductMixin, AvailableProductMixin):
    """
    Add this mixin class to the product models declaration, wanting to keep track on the
    current amount of products in stock.  In comparison to
    :class:`shop.models.product.AvailableProductMixin`, this mixin reserves items in pending
    carts, without the risk for overselling. On the other hand, the shop may run out of sellable
    items, if customers keep products in the cart for a long period, without proceeding to checkout.
    Use this mixin for products kept for a short period until checking out the cart, for
    instance for ticket sales. Ensure that pending carts are flushed regularly.
    """


class BaseInventory(models.Model):
    """
    This is a holder for the quantity of products items in stock.
    It also keeps track of the period, during which that product is available.

    The class implementing this abstract base class, must add a field named 'quantity'
    of type IntegerField, DecimalField or FloatField.
    """
    earliest = models.DateTimeField(
        _("Available after"),
        default=timezone.datetime.min.replace(tzinfo=timezone.get_current_timezone()),
        db_index=True,
    )

    latest = models.DateTimeField(
        _("Available before"),
        default=timezone.datetime.max.replace(tzinfo=timezone.get_current_timezone()),
        db_index=True,
    )

    class Meta:
        abstract = True
        verbose_name = _("Product Inventory")
        verbose_name_plural = _("Product Inventories")

    @classmethod
    def check(cls, **kwargs):
        from shop.models.cart import CartItemModel

        errors = super().check(**kwargs)
        for cart_field in CartItemModel._meta.fields:
            if cart_field.attname == 'quantity':
                break
        else:
            msg = "Class `{}` must implement a field named `quantity`."
            errors.append(checks.Error(msg.format(CartItemModel.__name__)))
        for field in cls._meta.fields:
            if field.attname == 'quantity':
                if field.get_internal_type() != cart_field.get_internal_type():
                    msg = "Field `{}.quantity` must be of same type as `{}.quantity`."
                    errors.append(checks.Error(msg.format(cls.__name__, CartItemModel.__name__)))
                break
        else:
            msg = "Class `{}` must implement a field named `quantity`."
            errors.append(checks.Error(msg.format(cls.__name__)))
        for field in cls._meta.fields:
            if field.attname == 'product_id':
                if field.get_internal_type() == 'ForeignKey':
                    if field.related_query_name() != 'inventory_set':
                        msg = "Class `{}.product` must have a related_name 'inventory_set'."
                        errors.append(checks.Error(msg.format(cls.__name__)))
                    break
                msg = "Class `{}.product` must be a foreign key pointing onto a Product model or variation of thereof."
                errors.append(checks.Error(msg.format(cls.__name__)))
        else:
            msg = "Class `{}` must implement a foreign key pointing onto a Product model or variation of thereof."
            errors.append(checks.Error(msg.format(cls.__name__)))
        return errors
