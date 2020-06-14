import warnings
from collections import OrderedDict

from django.core import checks
from django.db import models
from django.utils.translation import gettext_lazy as _

from shop import deferred
from shop.models.fields import JSONField
from shop.models.customer import CustomerModel
from shop.models.product import BaseProduct
from shop.modifiers.pool import cart_modifiers_pool
from shop.money import Money


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
        quantity = int(kwargs.pop('quantity', 1))

        # add a new item to the cart, or reuse an existing one, increasing the quantity
        watched = not quantity
        cart_item = product.is_in_cart(cart, watched=watched, **kwargs)
        if cart_item:
            if not watched:
                cart_item.quantity += quantity
            created = False
        else:
            cart_item = self.model(cart=cart, product=product, quantity=quantity, **kwargs)
            created = True

        cart_item.save()
        return cart_item, created

    def filter_cart_items(self, cart, request):
        """
        Use this method to fetch items for shopping from the cart. It rearranges the result set
        according to the defined modifiers.
        """
        cart_items = self.filter(cart=cart, quantity__gt=0).order_by('updated_at')
        for modifier in cart_modifiers_pool.get_all_modifiers():
            cart_items = modifier.arrange_cart_items(cart_items, request)
        return cart_items

    def filter_watch_items(self, cart, request):
        """
        Use this method to fetch items from the watch list. It rearranges the result set
        according to the defined modifiers.
        """
        watch_items = self.filter(cart=cart, quantity=0)
        for modifier in cart_modifiers_pool.get_all_modifiers():
            watch_items = modifier.arrange_watch_items(watch_items, request)
        return watch_items


class BaseCartItem(models.Model, metaclass=deferred.ForeignKeyBuilder):
    """
    This is a holder for the quantity of items in the cart and, obviously, a
    pointer to the actual Product being purchased
    """
    cart = deferred.ForeignKey(
        'BaseCart',
        on_delete=models.CASCADE,
        related_name='items',
    )

    product = deferred.ForeignKey(
        BaseProduct,
        on_delete=models.CASCADE,
    )

    product_code = models.CharField(
        _("Product code"),
        max_length=255,
        null=True,
        blank=True,
        help_text=_("Product code of added item."),
    )

    updated_at = models.DateTimeField(
        _("Updated at"),
        auto_now=True,
    )

    extra = JSONField(verbose_name=_("Arbitrary information for this cart item"))

    objects = CartItemManager()

    class Meta:
        abstract = True
        verbose_name = _("Cart item")
        verbose_name_plural = _("Cart items")

    @classmethod
    def check(cls, **kwargs):
        errors = super().check(**kwargs)
        allowed_types = ['IntegerField', 'SmallIntegerField', 'PositiveIntegerField',
                         'PositiveSmallIntegerField', 'DecimalField', 'FloatField']
        for field in cls._meta.fields:
            if field.attname == 'quantity':
                if field.get_internal_type() not in allowed_types:
                    msg = "Class `{}.quantity` must be of one of the types: {}."
                    errors.append(checks.Error(msg.format(cls.__name__, allowed_types)))
                break
        else:
            msg = "Class `{}` must implement a field named `quantity`."
            errors.append(checks.Error(msg.format(cls.__name__)))
        return errors

    def __init__(self, *args, **kwargs):
        # reduce the given fields to what the model actually can consume
        all_field_names = [field.name for field in self._meta.get_fields(include_parents=True)]
        model_kwargs = {k: v for k, v in kwargs.items() if k in all_field_names}
        super().__init__(*args, **model_kwargs)
        self.extra_rows = OrderedDict()
        self._dirty = True

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.cart.save(update_fields=['updated_at'])
        self._dirty = True

    def update(self, request):
        """
        Loop over all registered cart modifier, change the price per cart item and optionally add
        some extra rows.
        """
        if not self._dirty:
            return
        self.refresh_from_db()
        self.extra_rows = OrderedDict()  # reset the dictionary
        for modifier in cart_modifiers_pool.get_all_modifiers():
            modifier.process_cart_item(self, request)
        self._dirty = False

CartItemModel = deferred.MaterializedModel(BaseCartItem)


class CartManager(models.Manager):
    """
    The Model Manager for any Cart inheriting from BaseCart.
    """

    def get_from_request(self, request):
        """
        Return the cart for current customer.
        """
        if request.customer.is_visitor:
            raise self.model.DoesNotExist("Cart for visiting customer does not exist.")
        if not hasattr(request, '_cached_cart') or request._cached_cart.customer.user_id != request.customer.user_id:
            request._cached_cart, created = self.get_or_create(customer=request.customer)
        return request._cached_cart

    def get_or_create_from_request(self, request):
        has_cached_cart = hasattr(request, '_cached_cart')
        if request.customer.is_visitor:
            request.customer = CustomerModel.objects.get_or_create_from_request(request)
            has_cached_cart = False
        if not has_cached_cart or request._cached_cart.customer.user_id != request.customer.user_id:
            request._cached_cart, created = self.get_or_create(customer=request.customer)
        return request._cached_cart


class BaseCart(models.Model, metaclass=deferred.ForeignKeyBuilder):
    """
    The fundamental part of a shopping cart.
    """
    customer = deferred.OneToOneField(
        'BaseCustomer',
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name=_("Customer"),
    )

    created_at = models.DateTimeField(
        _("Created at"),
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        _("Updated at"),
        auto_now=True,
    )

    extra = JSONField(verbose_name=_("Arbitrary information for this cart"))

    # our CartManager determines the cart object from the request.
    objects = CartManager()

    class Meta:
        abstract = True
        verbose_name = _("Shopping Cart")
        verbose_name_plural = _("Shopping Carts")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # That will hold things like tax totals or total discount
        self.extra_rows = OrderedDict()
        self._cached_cart_items = None
        self._dirty = True

    def save(self, force_update=False, *args, **kwargs):
        if self.pk or force_update is False:
            super().save(force_update=force_update, *args, **kwargs)
        self._dirty = True

    def update(self, request, raise_exception=False):
        """
        This should be called after a cart item changed quantity, has been added or removed.

        It will loop over all items in the cart, and call all the configured cart modifiers.
        After this is done, it will compute and update the order's total and subtotal fields, along
        with any supplement added along the way by modifiers.

        Note that theses added fields are not stored - we actually want to
        reflect rebate and tax changes on the *cart* items, but we don't want
        that for the order items (since they are legally binding after the
        "purchase" button was pressed)
        """
        if not self._dirty:
            return

        if self._cached_cart_items:
            items = self._cached_cart_items
        else:
            items = CartItemModel.objects.filter_cart_items(self, request)

        # This calls all the pre_process_cart methods and the pre_process_cart_item for each item,
        # before processing the cart. This allows to prepare and collect data on the cart.
        for modifier in cart_modifiers_pool.get_all_modifiers():
            modifier.pre_process_cart(self, request, raise_exception)
            for item in items:
                modifier.pre_process_cart_item(self, item, request, raise_exception)

        self.extra_rows = OrderedDict()  # reset the dictionary
        self.subtotal = 0  # reset the subtotal
        for item in items:
            # item.update iterates over all cart modifiers and invokes method `process_cart_item`
            item.update(request)
            self.subtotal += item.line_total

        # Iterate over the registered modifiers, to process the cart's summary
        for modifier in cart_modifiers_pool.get_all_modifiers():
            for item in items:
                modifier.post_process_cart_item(self, item, request)
            modifier.process_cart(self, request)

        # This calls the post_process_cart method from cart modifiers, if any.
        # It allows for a last bit of processing on the "finished" cart, before
        # it is displayed
        for modifier in reversed(cart_modifiers_pool.get_all_modifiers()):
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

    def merge_with(self, other_cart):
        """
        Merge the contents of the other cart into this one, afterwards delete it.
        This is done item by item, so that duplicate items increase the quantity.
        """
        # iterate over the cart and add quantities for items from other cart considered as equal
        if self.id == other_cart.id:
            raise RuntimeError("Can not merge cart with itself")
        for item in self.items.all():
            other_item = item.product.is_in_cart(other_cart, extra=item.extra)
            if other_item:
                item.quantity += other_item.quantity
                item.save()
                other_item.delete()

        # the remaining items from the other cart are merged into this one
        other_cart.items.update(cart=self)
        other_cart.delete()

    def __str__(self):
        return "{}".format(self.pk) if self.pk else "(unsaved)"

    @property
    def num_items(self):
        """
        Returns the number of items in the cart.
        """
        return self.items.filter(quantity__gt=0).count()

    @property
    def total_quantity(self):
        """
        Returns the total quantity of all items in the cart.
        """
        aggr = self.items.aggregate(quantity=models.Sum('quantity'))
        return aggr['quantity'] or 0
        # if we would know, that self.items is already evaluated, then this might be faster:
        # return sum([ci.quantity for ci in self.items.all()])

    @property
    def is_empty(self):
        return self.num_items == 0 and self.total_quantity == 0

    def get_caption_data(self):
        warnings.warn("This method is deprecated")
        return {'num_items': self.num_items, 'total_quantity': self.total_quantity,
                'subtotal': self.subtotal, 'total': self.total}

    @classmethod
    def get_default_caption_data(cls):
        warnings.warn("This method is deprecated")
        return {'num_items': 0, 'total_quantity': 0, 'subtotal': Money(), 'total': Money()}

CartModel = deferred.MaterializedModel(BaseCart)
