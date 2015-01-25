# -*- coding: utf-8 -*-
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.aggregates import Count
from django.utils import six
from django.utils.encoding import python_2_unicode_compatible, force_text
from django.utils.translation import ugettext_lazy as _
from polymorphic.manager import PolymorphicManager
from polymorphic.polymorphic_model import PolymorphicModel
from polymorphic.base import PolymorphicModelBase
from shop.util.fields import CurrencyField
from .order import BaseOrderItem


class ProductManager(PolymorphicManager):
    """
    A more classic manager for Product filtering and manipulation.
    """
    def active(self):
        return self.filter(active=True)


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
        OrderItem = getattr(BaseOrderItem, 'materialized_model')

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
    materialized_model with it.
    For instance,``BaseProduct.materialized_model.objects.all()`` returns all available products
    from the shop.
    """
    def __new__(cls, name, bases, attrs):
        model = super(PolymorphicProductMetaclass, cls).__new__(cls, name, bases, attrs)
        if model._meta.abstract:
            return model
        for baseclass in bases:
            basename = baseclass.__name__
            # since base classes have no valid model.Manager, refer to the materialized Model class
            print 'class: {0} with base {1}'.format(name, basename)
            if isinstance(baseclass, cls):
                materialized_model = getattr(baseclass, 'materialized_model', None)
                if materialized_model is None:
                    baseclass.materialized_model = model
                else:
                    if issubclass(materialized_model, model):
                        # as the materialized model, use the most generic one
                        baseclass.materialized_model = model
                    elif not issubclass(model, materialized_model):
                        raise ImproperlyConfigured("Abstract base class %s has been associated already "
                            "with a model %s, which is different or not a submodel of %s." % (name, model, materialized_model))
                print 'Copy manager {0} to {1}'.format(name, basename)
        return model


@python_2_unicode_compatible
class BaseProduct(six.with_metaclass(PolymorphicProductMetaclass, PolymorphicModel)):
    """
    A basic product for the shop.

    Most of the already existing fields here should be generic enough to reside
    on the "base model" and not on an added property.
    """
    product_code = models.CharField(max_length=255, verbose_name=_("Product code"))
    active = models.BooleanField(default=False, verbose_name=_('Active'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))
    unit_price = CurrencyField(verbose_name=_('Unit price'))
    objects = ProductManager()

    class Meta:
        abstract = True
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

    def __str__(self):
        return force_text(self.product_code)

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.slug])

    def get_price(self):
        """
        Returns the price for this item (provided for extensibility).
        """
        return self.unit_price

    def get_name(self):
        """
        Returns the name of this Product (provided for extensibility).
        """
        return self.name

    def get_product_reference(self):
        """
        Returns product reference of this Product (provided for extensibility).
        """
        return unicode(self.pk)

    @property
    def can_be_added_to_cart(self):
        return self.active
