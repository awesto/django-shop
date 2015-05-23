# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from six import with_metaclass
from collections import OrderedDict
from hashlib import sha1
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.translation import ugettext_lazy as _
from jsonfield.fields import JSONField
from shop.modifiers.pool import cart_modifiers_pool
from .product import BaseProduct
from . import deferred


class CartItemManager(models.Manager):
    """
    Customized model manager for our CartItem model.
    """
    def get_or_create(self, **kwargs):
        """
        Create a unique cart item. If the same product exists already in the given cart,
        increase its quantity, if the product in the cart seems to be the same.
        """
        cart = kwargs.pop('cart')
        product = kwargs.pop('product')
        surplus = dict(**kwargs)
        cart_item, created = self.get_or_create_item(cart, product, surplus)
        for key, attr in surplus.items():
            setattr(cart_item, key, attr)
        cart_item.save()
        return cart_item, created

    def get_or_create_item(self, cart, product, surplus):
        quantity = int(surplus.pop('quantity'))
        try:
            cart_item = self.model.objects.get(cart=cart, product=product)
            cart_item.quantity += quantity
            created = False
        except self.model.DoesNotExist:
            cart_item = self.model(cart=cart, product=product, quantity=quantity)
            created = True
        return cart_item, created


class BaseCartItem(with_metaclass(deferred.ForeignKeyBuilder, models.Model)):
    """
    This is a holder for the quantity of items in the cart and, obviously, a
    pointer to the actual Product being purchased
    """
    cart = deferred.ForeignKey('BaseCart', related_name='items')
    quantity = models.IntegerField(validators=[MinValueValidator(0)])
    product = deferred.ForeignKey(BaseProduct)
    extra = JSONField(default={}, editable=False,
        verbose_name=_("Arbitrary information for this cart item"))

    objects = CartItemManager()

    class Meta:
        abstract = True
        verbose_name = _("Cart item")
        verbose_name_plural = _("Cart items")

    def __init__(self, *args, **kwargs):
        # That will hold extra fields to display to the user (ex. taxes, discount)
        super(BaseCartItem, self).__init__(*args, **kwargs)
        self.extra_rows = OrderedDict()
        self._dirty = True

    def save(self, *args, **kwargs):
        super(BaseCartItem, self).save(*args, **kwargs)
        self._dirty = True
        self.cart._dirty = True

    def update(self, request):
        """
        Loop over all registered cart modifier, change the price per cart item and optionally add
        some extra rows.
        """
        if not self._dirty:
            return
        self.extra_rows = OrderedDict()  # reset the dictionary
        for modifier in cart_modifiers_pool.get_all_modifiers():
            modifier.process_cart_item(self, request)
        self._dirty = False

CartItemModel = deferred.MaterializedModel(BaseCartItem)


class CartVariableItemManager(CartItemManager):
    """
    Customized model manager for our CartVariableItem model.
    """
    def get_or_create_item(self, cart, product, surplus):
        quantity = int(surplus.pop('quantity'))
        variation = surplus.pop('variation', None)
        variation_hash = variation and sha1(json.dumps(variation, cls=DjangoJSONEncoder, sort_keys=True)).hexdigest()
        try:
            cart_item = self.model.objects.get(cart=cart, product=product, variation_hash=variation_hash)
            cart_item.quantity += quantity
            created = False
        except self.model.DoesNotExist:
            cart_item = self.model(cart=cart, product=product, variation_hash=variation_hash, quantity=quantity)
            created = True
        return cart_item, created


class BaseCartVariableItem(BaseCartItem):
    """
    Use this enriched implementation, in case a Product can be added to the cart in different
    variations.
    """
    variation = JSONField(null=True, blank=True,
        verbose_name=_("Configured product variation"))
    variation_hash = models.CharField(max_length=64, null=True,
        verbose_name=_("A hash for the above variation"))

    objects = CartVariableItemManager()

    class Meta:
        abstract = True


class CartManager(models.Manager):
    def get_from_request(self, request):
        """
        Return the cart for current user. Anonymous users also must have a primary key,
        thats why djangoSHOP requires its own authentication middleware.
        """
        cart = self.get_or_create(user=request.user)[0]
        return cart


class BaseCart(with_metaclass(deferred.ForeignKeyBuilder, models.Model)):
    """
    The fundamental parts of a shopping cart. It refers to a rather simple list of items.
    Ideally it should be bound to a session and not to a User is we want to let
    people buy from our shop without having to register with us.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))
    extra = JSONField(default={}, editable=False,
        verbose_name=_("Arbitrary information for this cart"))

    # our CartManager determines the cart object from the request.
    objects = CartManager()

    class Meta:
        abstract = True
        verbose_name = _("Shopping Cart")
        verbose_name_plural = _("Shopping Carts")

    def __init__(self, *args, **kwargs):
        super(BaseCart, self).__init__(*args, **kwargs)
        # That will hold things like tax totals or total discount
        self.extra_rows = OrderedDict()
        self._cached_cart_items = None
        self._dirty = True

    def save(self, *args, **kwargs):
        super(BaseCart, self).save(*args, **kwargs)
        self._dirty = True

    def update(self, request):
        """
        This should be called after a cart item changed quantity, has been added or removed.

        It will loop on all line items in the cart, and call all the cart modifiers for each item.
        After doing this, it will compute and update the order's total and subtotal fields, along
        with any supplement added along the way by modifiers.

        Note that theses added fields are not stored - we actually want to
        reflect rebate and tax changes on the *cart* items, but we don't want
        that for the order items (since they are legally binding after the
        "purchase" button was pressed)
        """
        if not self._dirty:
            return

        items = CartItemModel.objects.filter(cart=self, quantity__gt=0).order_by('pk')

        # The request object holds extra information in a dict named 'cart_modifier_state'.
        # Cart modifiers can use this dict to pass arbitrary data from and to each other.
        if not hasattr(request, 'cart_modifier_state'):
            setattr(request, 'cart_modifier_state', {})

        # This calls all the pre_process_cart methods (if any), before the cart is processed.
        # This for example allows for data collection on the cart.
        for modifier in cart_modifiers_pool.get_all_modifiers():
            modifier.pre_process_cart(self, request)

        self.extra_rows = OrderedDict()  # reset the dictionary
        self.subtotal = 0  # reset the subtotal
        for item in items:
            # item.update iterates over all cart modifiers and invokes method `process_cart_item`
            item.update(request)
            self.subtotal += item.line_total

        # Iterate over the registered modifiers, to process the cart's summary
        for modifier in cart_modifiers_pool.get_all_modifiers():
            modifier.process_cart(self, request)

        # This calls the post_process_cart method from cart modifiers, if any.
        # It allows for a last bit of processing on the "finished" cart, before
        # it is displayed
        for modifier in cart_modifiers_pool.get_all_modifiers():
            modifier.post_process_cart(self, request)

        # Cache updated cart items
        self._cached_cart_items = items
        self._dirty = False

    def empty(self):
        """
        Remove the cart with all its items.
        """
        if self.pk:
            self.items.all().delete()
            self.delete()

    @property
    def total_quantity(self):
        """
        Returns the total quantity of all items in the cart.
        """
        return sum([ci.quantity for ci in self.items.all()])

    @property
    def is_empty(self):
        return self.total_quantity == 0

CartModel = deferred.MaterializedModel(BaseCart)
