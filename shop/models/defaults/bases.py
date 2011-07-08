# -*- coding: utf-8 -*-
from decimal import Decimal
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from shop.cart.modifiers_pool import cart_modifiers_pool
from shop.models.productmodel import Product

class BaseCart(models.Model):
    """
    This should be a rather simple list of items. Ideally it should be bound to
    a session and not to a User is we want to let people buy from our shop
    without having to register with us.
    """
    # If the user is null, that means this is used for a session
    user = models.OneToOneField(User, null=True, blank=True)

    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta(object):
        abstract = True
        app_label = 'shop'
        verbose_name = _('Cart')
        verbose_name_plural = _('Carts')

    def __init__(self, *args, **kwargs):
        super(Cart, self).__init__(*args,**kwargs)
        # That will hold things like tax totals or total discount
        self.subtotal_price = Decimal('0.0')
        self.total_price = Decimal('0.0')
        self.extra_price_fields = [] # List of tuples (label, value)

    def add_product(self, product, quantity=1, merge=True, queryset=None):
        """
        Adds a (new) product to the cart.

        The parameter `merge`, controls wheter we should merge the added
        CartItem with another already existing sharing the same
        product_id. This is useful when you have products with variations
        (for example), and you don't want to have your products merge (to loose
        their specific variations, for example).

        A drawback is, that generally  setting `merge` to ``False`` for products
        with variations can be a problem if users can buy thousands of products
        at a time (that would mean we would create thousands of CartItems as
        well which all have the same variation).

        The parameter `queryset` can be used to override the standard queryset
        that is being used to find the CartItem that should be merged into.
        If you use variations, just finding the first CartItem that
        belongs to this cart and the given product is not sufficient. You will
        want to find the CartItem that already has the same variations that the
        user chose for this request.

        Example with merge = True:
        >>> self.items[0] = CartItem.objects.create(..., product=MyProduct())
        >>> self.add_product(MyProduct())
        >>> self.items[0].quantity
        2

        Example with merge=False:
        >>> self.items[0] = CartItem.objects.create(..., product=MyProduct())
        >>> self.add_product(MyProduct())
        >>> self.items[0].quantity
        1
        >>> self.items[1].quantity
        1
        """
        if queryset == None:
            queryset = CartItem.objects.filter(cart=self, product=product)
        item = queryset
        # Let's see if we already have an Item with the same product ID
        if item.exists() and merge:
            cart_item = item[0]
            cart_item.quantity = cart_item.quantity + int(quantity)
            cart_item.save()
        else:
            cart_item = CartItem.objects.create(
                cart=self, quantity=quantity, product=product)
            cart_item.save()

        self.save() # to get the last updated timestamp
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

    def delete_item(self, cart_item_id):
        """
        A simple convenience method to delete one of the cart's items. This
        allows to implicitely check for "access rights" since we insure the cartitem
        is actually in the user's cart
        """
        cart_item = self.items.get(pk=cart_item_id)
        cart_item.delete()
        self.save()

    def update(self):
        """
        This should be called whenever anything is changed in the cart (added or removed)
        It will loop on all line items in the cart, and call all the price modifiers
        on each row.
        After doing this, it will compute and update the order's total and
        subtotal fields, along with any payment field added along the way by
        modifiers.

        Note that theses added fields are not stored - we actually want to reflect
        rebate and tax changes on the *cart* items, but we don't want that for
        the order items (since they are legally binding after the "purchase" button
        was pressed)
        """
        items = CartItem.objects.filter(cart=self)
        self.subtotal_price = Decimal('0.0') # Reset the subtotal

        for item in items: # For each OrderItem (order line)...
            self.subtotal_price = self.subtotal_price + item.update()
            item.save()

        # Now we have to iterate over the registered modifiers again (unfortunately)
        # to pass them the whole Order this time
        for modifier in cart_modifiers_pool.get_modifiers_list():
            modifier.process_cart(self)

        self.total_price = self.subtotal_price
        # Like for line items, most of the modifiers will simply add a field
        # to extra_price_fields, let's update the total with them
        for label, value in self.extra_price_fields:
            self.total_price = self.total_price + value

    def empty(self):
        """
        Remove all cart items
        """
        self.items.all().delete()
        self.delete()

    @property
    def total_quantity(self):
        """
        Returns the total quantity of all items in the cart
        """
        return sum([ci.quantity for ci in self.items.all()])


class BaseCartItem(models.Model):
    """
    This is a holder for the quantity of items in the cart and, obviously, a
    pointer to the actual Product being purchased :)
    """
    cart = models.ForeignKey(Cart, related_name="items")

    quantity = models.IntegerField()

    product = models.ForeignKey(Product)

    class Meta(object):
        abstract = True
        app_label = 'shop'
        verbose_name = _('Cart item')
        verbose_name_plural = _('Cart items')

    def __init__(self, *args, **kwargs):
        # That will hold extra fields to display to the user
        # (ex. taxes, discount)
        super(CartItem, self).__init__(*args,**kwargs)
        self.extra_price_fields = [] # list of tuples (label, value)
        # These must not be stored, since their components can be changed between
        # sessions / logins etc...
        self.line_subtotal = Decimal('0.0')
        self.line_total = Decimal('0.0')

    def update(self):
        self.line_subtotal = self.product.get_price() * self.quantity
        self.line_total = self.line_subtotal

        for modifier in cart_modifiers_pool.get_modifiers_list():
            # We now loop over every registered price modifier,
            # most of them will simply add a field to extra_payment_fields
            modifier.process_cart_item(self)

        for label, value in self.extra_price_fields:
            self.line_total = self.line_total + value

        return self.line_total