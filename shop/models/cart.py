# -*- coding: utf-8 -*-
import json
from six import with_metaclass
from collections import namedtuple
from decimal import Decimal
from hashlib import sha1
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.translation import ugettext_lazy as _
from jsonfield.fields import JSONField
from shop.cart.modifiers_pool import cart_modifiers_pool
from .product import BaseProduct
from . import deferred


class BaseCartItem(with_metaclass(deferred.ForeignKeyBuilder, models.Model)):
    """
    This is a holder for the quantity of items in the cart and, obviously, a
    pointer to the actual Product being purchased :)
    """
    class Meta:
        abstract = True
        verbose_name = _("Cart item")
        verbose_name_plural = _("Cart items")

    # the inheriting class may override this and add additional values to this dataset
    ExtraItemRow = namedtuple('ExtraItemRow', ('label', 'amount',))

    cart = deferred.ForeignKey('BaseCart', related_name='items')
    quantity = models.IntegerField()
    product = deferred.ForeignKey(BaseProduct)

    def __init__(self, *args, **kwargs):
        # That will hold extra fields to display to the user (ex. taxes, discount)
        super(BaseCartItem, self).__init__(*args, **kwargs)
        self.extra_item_rows = []  # list of ExtraItemRow
        # These must not be stored, since their components can be changed
        # between sessions / logins etc...
        self.line_subtotal = Decimal('0.0')
        self.line_total = Decimal('0.0')
        self.current_total = Decimal('0.0')  # Used by cart modifiers

    def update(self, request):
        self.extra_item_rows = []  # Reset the price fields
        self.line_subtotal = self.product.get_price() * self.quantity
        self.current_total = self.line_subtotal

        for modifier in cart_modifiers_pool.get_modifiers_list():
            # We now loop over every registered price modifier,
            # most of them will simply add a field to extra_payment_fields
            modifier.process_cart_item(self, request)

        self.line_total = self.current_total
        return self.line_total


class BaseCartVariableItem(BaseCartItem):
    """
    This is an enriched implementation, in case your products allow variations.
    """
    class Meta:
        abstract = True

    variation = JSONField(null=True, blank=True,
        verbose_name=_("Configured product variation"))
    variation_hash = models.CharField(max_length=64, null=True,
        verbose_name=_("A hash for the above variation"))


class CartManager(models.Manager):
    def get_from_request(self, request):
        """
        Return the cart for current visitor. The visitor is determined through the request object.
        If the visitor is logged in, find the cart through the user model. Otherwise use its
        session_key. If no cart object was found, create an empty one and return it.
        """
        if request.user.is_authenticated():
            try:
                cart = self.get(user=request.user)
            except self.model.DoesNotExist:
                cart, _ = self.get_or_create(user=request.user, session_key=request.session.session_key)
        else:
            try:
                cart = self.get(session_key=request.session.session_key)
            except self.model.DoesNotExist:
                cart, _ = self.get_or_create(user=AnonymousUser.id, session_key=request.session.session_key)
        return cart


class BaseCart(with_metaclass(deferred.ForeignKeyBuilder, models.Model)):
    """
    The fundamental parts of a shopping cart. It refers to a rather simple list of items.
    Ideally it should be bound to a session and not to a User is we want to let
    people buy from our shop without having to register with us.
    """
    class Meta:
        abstract = True
        verbose_name = _("Shopping Cart")
        verbose_name_plural = _("Shopping Carts")

    # the inheriting class may override this and add additional values to this dataset
    ExtraRow = namedtuple('ExtraRow', ('label', 'amount',))

    # If user is None, this cart is associated with a session
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, default=None)
    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    objects = CartManager()

    def __init__(self, *args, **kwargs):
        super(BaseCart, self).__init__(*args, **kwargs)
        # That will hold things like tax totals or total discount
        self.subtotal_price = Decimal('0.0')
        self.total_price = Decimal('0.0')
        self.current_total = Decimal('0.0')  # used by cart modifiers
        self.extra_rows = []  # list of ExtraRow
        self._updated_cart_items = None

    def add_product(self, product, quantity=1, variation=None):
        """
        Adds a (new) product to the cart.

        The parameter `variation`, can be any kind of JSON serializable Python
        object.
        If a product with exactly this variation already exists, the quantity
        is increased in the cart. Otherwise a new product is added to the cart.
        """
        # check if product can be added at all
        if not product.get_availability():
            return None

        CartItemModel = getattr(BaseCartItem, 'MaterializedModel')

        # search for an item with the same product and the same variation, otherwise create it
        if hasattr(CartItemModel, 'variation_hash'):
            variation_hash = variation and sha1(json.dumps(variation, cls=DjangoJSONEncoder, sort_keys=True)).hexdigest()
            cart_item, created = CartItemModel.objects.get_or_create(cart=self, product=product, variation_hash=variation_hash)
        else:
            cart_item, created = CartItemModel.objects.get_or_create(cart=self, product=product)
        if created:
            cart_item.quantity = int(quantity)
        else:
            cart_item.quantity += int(quantity)
        cart_item.save()
        return cart_item

    def update_quantity(self, cart_item_id, quantity):
        """
        Updates the quantity for given cart item or deletes it if its quantity
        reaches `0`
        """
        cart_item = self.items.get(pk=cart_item_id)
        if quantity == 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()
        self.save()
        return cart_item

    def delete_item(self, cart_item_id):
        """
        A simple convenience method to delete one of the cart's items.
        This allows to implicitly check for "access rights" since we insure the
        CartItem is actually in the user's cart.
        """
        cart_item = self.items.get(pk=cart_item_id)
        cart_item.delete()
        self.save()

    def get_updated_cart_items(self):
        """
        Returns updated cart items after update() has been called and
        cart modifiers have been processed for all cart items.
        """
        assert self._updated_cart_items is not None, ('Cart needs to be '
            'updated before calling get_updated_cart_items.')
        return self._updated_cart_items

    def update(self, request):
        """
        This should be called whenever anything is changed in the cart (added
        or removed).

        It will loop on all line items in the cart, and call all the price
        modifiers on each row.
        After doing this, it will compute and update the order's total and
        subtotal fields, along with any payment field added along the way by
        modifiers.

        Note that theses added fields are not stored - we actually want to
        reflect rebate and tax changes on the *cart* items, but we don't want
        that for the order items (since they are legally binding after the
        "purchase" button was pressed)
        """
        CartItemModel = getattr(BaseCartItem, 'MaterializedModel')

        # This is a ghetto "select_related" for polymorphic models.
        items = CartItemModel.objects.filter(cart=self).order_by('pk')
        product_ids = [item.product_id for item in items]
        products = BaseProduct.objects.filter(pk__in=product_ids)
        products_dict = dict([(p.pk, p) for p in products])

        self.extra_rows = []  # Reset list of ExtraRows
        self.subtotal_price = Decimal('0.0')  # Reset the subtotal

        # The request object holds extra information in a dict named 'cart_modifier_state'.
        # Cart modifiers can use this dict to pass arbitrary data from and to each other.
        if not hasattr(request, 'cart_modifier_state'):
            setattr(request, 'cart_modifier_state', {})

        # This calls all the pre_process_cart methods (if any), before the cart
        # is processed. This allows for data collection on the cart for
        # example)
        for modifier in cart_modifiers_pool.get_modifiers_list():
            modifier.pre_process_cart(self, request)

        for item in items:  # For each CartItem (order line)...
            # This is still the ghetto select_related
            item.product = products_dict[item.product_id]
            self.subtotal_price = self.subtotal_price + item.update(request)

        self.current_total = self.subtotal_price
        # Now we have to iterate over the registered modifiers again
        # (unfortunately) to pass them the whole Order this time
        for modifier in cart_modifiers_pool.get_modifiers_list():
            modifier.process_cart(self, request)

        self.total_price = self.current_total

        # This calls the post_process_cart method from cart modifiers, if any.
        # It allows for a last bit of processing on the "finished" cart, before
        # it is displayed
        for modifier in cart_modifiers_pool.get_modifiers_list():
            modifier.post_process_cart(self, request)

        # Cache updated cart items
        self._updated_cart_items = items

    def empty(self):
        """
        Remove all cart items
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
