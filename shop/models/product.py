# -*- coding: utf-8 -*-
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models.aggregates import Count
from django.utils import six
from django.utils.encoding import python_2_unicode_compatible, force_text
from django.utils.translation import ugettext_lazy as _
from polymorphic.manager import PolymorphicManager
from polymorphic.polymorphic_model import PolymorphicModel
from polymorphic.base import PolymorphicModelBase
from .order import BaseOrderItem


class ProductStatisticsManager(PolymorphicManager):
    """
    A Manager for all the non-object manipulation needs, mostly statistics and
    other "data-mining" toys.
    """

    def top_selling_products(self, quantity):
        """
        This method "mines" the previously passed orders, and gets a list of
        products (of a size equal to the quantity parameter), ordered by how
        many times they have been purchased.
        """
        OrderItem = getattr(BaseOrderItem, 'MaterializedModel')

        # Get an aggregate of product references and their respective counts
        top_products_data = OrderItem.objects.values('product') \
            .annotate(product_count=Count('product')) \
            .order_by('product_count')[:quantity]

        # The top_products_data result should be in the form:
        # [{'product_reference': '<product_id>', 'product_count': <count>}, ..]

        top_products_list = []  # The actual list of products
        for values in top_products_data:
            prod = values.get('product')
            # We could eventually return the count easily here, if needed.
            top_products_list.append(prod)

        return top_products_list


class PolymorphicProductMetaclass(PolymorphicModelBase):
    """
    The BaseProduct class must refer to their materialized model definition, for instance when
    accessing its model manager. Since polymoriphic product classes, normally are materialized
    by more than one model, this metaclass finds the most generic one and associates its
    MaterializedModel with it.
    For instance,``BaseProduct.MaterializedModel.objects.all()`` returns all available products
    from the shop.
    """
    def __new__(cls, name, bases, attrs):
        Model = super(PolymorphicProductMetaclass, cls).__new__(cls, name, bases, attrs)
        if Model._meta.abstract:
            return Model
        for baseclass in bases:
            # since an abstract base class does not have no valid model.Manager,
            # refer to it via a MaterializedModel.
            if isinstance(baseclass, cls):
                try:
                    if issubclass(baseclass.MaterializedModel, Model):
                        # as the materialized model, use the most generic one
                        baseclass.MaterializedModel = Model
                    elif not issubclass(Model, baseclass.MaterializedModel):
                        raise ImproperlyConfigured("Abstract base class {0} has been associated already "
                            "with a model {1}, which is different or not a submodel of {2}." %
                            (name, Model, baseclass.MaterializedModel))
                except (AttributeError, TypeError):
                    baseclass.MaterializedModel = Model
        return Model


@python_2_unicode_compatible
class BaseProduct(six.with_metaclass(PolymorphicProductMetaclass, PolymorphicModel)):
    """
    A basic product for the shop.

    Most of the already existing fields here should be generic enough to reside
    on the "base model" and not on an added property.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))
    objects = PolymorphicManager()

    class Meta:
        abstract = True
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self):
        return force_text(self.get_name())

    def product_type(self):
        """
        Returns the polymorphic type of the product.
        """
        return force_text(self.polymorphic_ctype)
    product_type.short_description = _("Product type")

    def get_absolute_url(self):
        """
        Hook for returning the canonical URL of this product.
        """
        raise NotImplementedError('Method get_absolute_url() must be implemented by subclass: {0}'.format(self.__class__.__name__))

    def get_name(self):
        """
        Hook for returning the spoken name of this product.
        """
        raise NotImplementedError('Method get_name() must be implemented by subclass: {0}'.format(self.__class__.__name__))

    def get_reference(self):
        """
        Hook for returning the unique reference of this product.
        """
        raise NotImplementedError('Method get_reference() must be implemented by subclass: {0}'.format(self.__class__.__name__))

    def get_price(self, request):
        """
        Hook for returning the current price of this product.
        """
        raise NotImplementedError('Method get_price() must be implemented by subclass: {0}'.format(self.__class__.__name__))

    @property
    def is_available(self):
        """
        Hook for returning the availability of a product.
        """
        return True
