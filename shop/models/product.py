# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
from functools import reduce
import operator
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils import six
from django.utils.encoding import force_text
from django.utils.six.moves.urllib.parse import urljoin
from django.utils.translation import ugettext_lazy as _
from polymorphic.manager import PolymorphicManager
from polymorphic.models import PolymorphicModel
from polymorphic.base import PolymorphicModelBase
from shop import deferred


class BaseProductManager(PolymorphicManager):
    """
    A base ModelManager for all non-object manipulation needs, mostly statistics and querying.
    """
    def select_lookup(self, search_term):
        """
        Returning a queryset containing the products matching the declared lookup fields together
        with the given search term. Each product can define its own lookup fields using the
        member list or tuple `lookup_fields`.
        """
        filter_by_term = (models.Q((sf, search_term)) for sf in self.model.lookup_fields)
        queryset = self.get_queryset().filter(reduce(operator.or_, filter_by_term))
        return queryset

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
                    baseclass._materialized_model = Model
                elif not issubclass(Model, baseclass._materialized_model):
                    raise ImproperlyConfigured("Abstract base class {} has already been associated "
                        "with a model {}, which is different or not a submodel of {}."
                        .format(name, Model, baseclass._materialized_model))
            except (AttributeError, TypeError):
                baseclass._materialized_model = Model

            # check for pending mappings in the ForeignKeyBuilder and in case, process them
            deferred.ForeignKeyBuilder.process_pending_mappings(Model, baseclass.__name__)

        deferred.ForeignKeyBuilder.handle_deferred_foreign_fields(Model)
        cls.perform_model_checks(Model)
        return Model

    @classmethod
    def perform_model_checks(cls, Model):
        """
        Perform some safety checks on the ProductModel being created.
        """
        if not isinstance(Model.objects, BaseProductManager):
            msg = "Class `{}.objects` must provide ModelManager inheriting from BaseProductManager"
            raise NotImplementedError(msg.format(Model.__name__))

        if not isinstance(getattr(Model, 'lookup_fields', None), (list, tuple)):
            msg = "Class `{}` must provide a tuple of `lookup_fields` so that we can easily lookup for Products"
            raise NotImplementedError(msg.format(Model.__name__))

        try:
            # properties and translated fields are available through the class
            Model.product_name
        except AttributeError:
            try:
                # model fields are only available through a class instance
                Model().product_name
            except AttributeError:
                msg = "Class `{}` must provide a model field implementing `product_name`"
                raise NotImplementedError(msg.format(Model.__name__))

        if not callable(getattr(Model, 'get_price', None)):
            msg = "Class `{}` must provide a method implementing `get_price(request)`"
            raise NotImplementedError(msg.format(cls.__name__))


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

    Unless each product variant offers it's own product code, it is strongly recommended to add
    a field ``product_code = models.CharField(_("Product code"), max_length=255, unique=True)``
    to the class implementing the product.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))
    active = models.BooleanField(default=True, verbose_name=_("Active"),
        help_text=_("Is this product publicly visible."))

    class Meta:
        abstract = True
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

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

    def is_in_cart(self, cart, watched=False, **kwargs):
        """
        Checks if the current product is already in the given cart, and if so, returns the
        corresponding cart_item.

        Args:
            watched (bool): This is used to determine if this check shall only be performed
                for the watch-list.

            **kwargs: Optionally one may pass arbitrary information about the product being looked
                 up. This can be used to determine if a product with variations shall be considered
                 equal to the same cart item, resulting in an increase of it's quantity, or if it
                 shall be considered as a separate cart item, resulting in the creation of a new
                 item.

        Returns:
            The cart_item containing the product considered as equal to the current one, or
            ``None`` if it is not available.
        """
        from .cart import CartItemModel
        cart_item_qs = CartItemModel.objects.filter(cart=cart, product=self)
        return cart_item_qs.first()

ProductModel = deferred.MaterializedModel(BaseProduct)


class CMSPageReferenceMixin(object):
    """
    Products which refer to CMS pages in order to emulate categories, normally need
    a way to be accessed directly via a URL. Add this mixin to Product classes to
    add a ``get_absolute_url()`` method.
    """
    def get_absolute_url(self):
        """
        Return the absolute URL of a product
        """
        # sorting by highest level, so that the canonical URL
        # associates with the most generic category
        cms_page = self.cms_pages.order_by('depth').last()
        if cms_page is None:
            return urljoin('/category-not-assigned/', self.slug)
        return urljoin(cms_page.get_absolute_url(), self.slug)
