# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils import six
from django.utils.encoding import python_2_unicode_compatible, force_text
from django.utils.translation import ugettext_lazy as _
from polymorphic.manager import PolymorphicManager
from polymorphic.polymorphic_model import PolymorphicModel
from polymorphic.base import PolymorphicModelBase
from . import deferred


class BaseProductManager(PolymorphicManager):
    """
    A base ModelManager for all non-object manipulation needs, mostly statistics and querying.
    """
    def select_lookup(self, search_term):
        """
        Hook for returning a queryset containing the products matching the lookup criteria given
        be the search term. This method must be implemented by the ProductManager used by the
        real model implementing the product.
        """
        msg = "Method select_lookup() must be implemented by subclass: `{}`"
        raise NotImplementedError(msg.format(self.__class__.__name__))

    def indexable(self):
        """
        Return a queryset of indexable Products.
        """
        queryset = self.get_queryset().filter(active=True)
        return queryset


class PolymorphicProductMetaclass(PolymorphicModelBase):
    """
    The BaseProduct class must refer to their materialized model definition, for instance when
    accessing its model manager. Since polymoriphic product classes, normally are materialized
    by more than one model, this metaclass finds the most generic one and associates its
    MaterializedModel with it.
    For instance,``ProductModel.objects.all()`` returns all available products from the shop.
    """
    def __new__(cls, name, bases, attrs):
        Model = super(PolymorphicProductMetaclass, cls).__new__(cls, name, bases, attrs)
        if Model._meta.abstract:
            return Model
        for baseclass in bases:
            # since an abstract base class does not have no valid model.Manager,
            # refer to it via its materialized Product model.
            if not isinstance(baseclass, cls):
                continue
            try:
                if issubclass(baseclass._materialized_model, Model):
                    # as the materialized model, use the most generic one
                    cls.check_fields(Model, attrs)
                    baseclass._materialized_model = Model
                elif not issubclass(Model, baseclass._materialized_model):
                    raise ImproperlyConfigured("Abstract base class {} has already been associated "
                        "with a model {}, which is different or not a submodel of {}."
                        .format(name, Model, baseclass._materialized_model))
            except (AttributeError, TypeError):
                cls.check_fields(Model, attrs)
                baseclass._materialized_model = Model

            # check for pending mappings in the ForeignKeyBuilder and in case, process them
            deferred.ForeignKeyBuilder.process_pending_mappings(Model, baseclass.__name__)
        return Model

    @classmethod
    def check_fields(cls, Model, attrs):
        if not isinstance(attrs.get('product_name'), (models.Field, property)):
            msg = "Class `{}` must provide a model field or property implementing `product_name`"
            raise NotImplementedError(msg.format(Model.__name__))


@python_2_unicode_compatible
class BaseProduct(six.with_metaclass(PolymorphicProductMetaclass, PolymorphicModel)):
    """
    An abstract basic product model for the shop. It is intended to be overridden by one or
    more polymorphic models, adding all the fields and relations, required to describe this
    type of product.

    Some attributes for this class are mandatory. They shall be implemented as property method.
    The following fields MUST be implemented by the inheriting class:
    `product_name`: Return the pronounced name for this product in its localized language.

    Additionally the inheriting class MUST implement the following methods `get_absolute_url()`
    and `get_price()`. See below for details.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))
    active = models.BooleanField(default=True, verbose_name=_("Active"),
        help_text=_("Is this product publicly visible."))

    objects = BaseProductManager()

    class Meta:
        abstract = True
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self):
        return self.product_name

    def product_type(self):
        """
        Returns the polymorphic type of the product.
        """
        return force_text(self.polymorphic_ctype)
    product_type.short_description = _("Product type")

    @property
    def product_model(self):
        """
        Returns the polymorphic model name of the product's class.
        """
        return self.polymorphic_ctype.model

    def get_absolute_url(self):
        """
        Hook for returning the canonical Django URL of this product.
        """
        msg = "Method get_absolute_url() must be implemented by subclass: `{}`"
        raise NotImplementedError(msg.format(self.__class__.__name__))

    def get_price(self, request):
        """
        Hook for returning the current price of this product.
        The price shall be of type Money. Read the appropriate section on how to create a Money
        type for the chosen currency.
        Use the `request` object to vary the price according to the logged in user,
        its country code or the language.
        """
        msg = "Method get_price() must be implemented by subclass: `{}`"
        raise NotImplementedError(msg.format(self.__class__.__name__))

    def get_availability(self, request):
        """
        Hook for checking the availability of a product. It returns a list of tuples with this
        notation:
        - Number of items available for this product until the specified period expires.
          If this value is ``True``, then infinitely many items are available.
        - Until which timestamp, in UTC, the specified number of items are available.
        This function can return more than one tuple. If the list is empty, then the product is
        considered as not available.
        Use the `request` object to vary the availability according to the logged in user,
        its country code or language.
        """
        return [(True, datetime.max)]  # Infinite number of products available until eternity

    def is_in_cart(self, cart, extra, watched=False):
        """
        Checks if the product is already in the given cart, and if so, returns the corresponding
        cart_item, otherwise this method returns None. The dictionary `extra` is  used for passing
        arbitrary information about the product. It can be used to determine if products with
        variations shall be added to the cart or added as separate items.
        The boolean `watched` can be used to determine if this check shall only be performed for
        the watch-list.
        """
        from .cart import CartItemModel
        cart_item_qs = CartItemModel.objects.filter(cart=cart, product=self)
        return cart_item_qs.first()

ProductModel = deferred.MaterializedModel(BaseProduct)
