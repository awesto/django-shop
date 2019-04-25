.. _tutorial/product-model-smartcard:

The Smart Card Product Model
============================

The demo provided by cookiecutter-django-shop_ using the product model "smartcard", shows how to
setup a shop, with a single product type. In our example we use a Smart Card for it. Here the Django
model is managed by the merchant implementation.

Smart Cards have many different attributes such as their card type, the manufacturer, storage
capacity and the maximum transfer speed. Here it's the merchant's responsibility to create the
database model according to the physical properties of the product. The model class to describe a
Smart Card therefore is not part of the shop's framework, but rather in the merchant's
implementation as found in our example.

Creating a customized product model, requires only a few lines of declarative Python code. Here is a
simplified example:

.. code-block:: python

	from django.db import models
	from shop.models.product import BaseProduct, BaseProductManager, CMSPageReferenceMixin
	from shop.money.fields import MoneyField

	class SmartCard(CMSPageReferenceMixin, BaseProduct):
	    product_name = models.CharField(
	        max_length=255,
	        verbose_name="Product Name",
	    )

	    slug = models.SlugField(verbose_name="Slug")

	    caption = models.TextField(
	        "Caption",
	        help_text="Short description used in the catalog's list view.",
	    )

	    description = models.TextField(
	        "Description",
	        help_text="Long description used in the product's detail view.",
	    )

	    order = models.PositiveIntegerField(
	        "Sort by",
	        db_index=True,
	    )

	    cms_pages = models.ManyToManyField(
	        'cms.Page',
	        through=ProductPage,
	        help_text="Choose list view this product shall appear on.",
	    )

	    images = models.ManyToManyField(
	        'filer.Image',
	        through=ProductImage,
	    )

	    unit_price = MoneyField(
	        "Unit price",
	        decimal_places=3,
	        help_text="Net price for this product",
	    )

	    card_type = models.CharField(
	        "Card Type",
	        choices=[(t, t) for t in ('SD', 'SDXC', 'SDHC', 'SDHC II')],
	        max_length=9,
	    )

	    product_code = models.CharField(
	        "Product code",
	        max_length=255,
	        unique=True,
	    )

	    storage = models.PositiveIntegerField(
	        "Storage Capacity",
	        help_text="Storage capacity in GB",
	    )

	    class Meta:
	        verbose_name = "Smart Card"
	        verbose_name_plural = "Smart Cards"
	        ordering = ['order']

	    lookup_fields = ['product_code__startswith', 'product_name__icontains']

	    objects = BaseProductManager()

	    def get_price(self, request):
	        return self.unit_price

	    def __str__(self):
	        return self.product_name

	    @property
	    def sample_image(self):
	        return self.images.first()


Let's examine this product model. Our ``SmartCard`` inherits from the abstract
:class:`shop.models.product.BaseProduct`, which is the base class for any product. It only contains
a minimal amount of fields, because **django-SHOP** doesn't make any assumptions about the product's
properties. Additionally this class inherits from the mixin
:class:`shop.models.product.CMSPageReferenceMixin`, which adds some functionality to handle CMS
pages as product categories.

In this class declaration, we use one field for each physical property of our Smart Cards, such as
card type, storage, transfer speed, etc. Using one field per property allows us to build much
simpler interfaces, rather than e-commerce solutions, which use a one-size-fits-all approach,
attempting to represent all product's properties. Otherwise, this product model class behaves
exactly like any other `Django model`_.

In addition to the properties, the example above contains these extra fields:

* ``slug``: This is the URL part after the category part.
* ``order``: This is an integer field to remember the sorting order of products.
* ``cms_pages``: A list of CMS pages, this product shall appear on.
* ``images``: A list of images of this product.

The list in ``lookup_fields`` is used by the Select2-widget, when searching for a product. This is
often required, while setting internal links onto products.

In **django-SHOP**, the field ``unit_price`` is optional. Instead, each product class must provide a
method ``get_price()``, which shall return the unit price for the catalog's list view. This is
because products may have variations with different price tags, or prices for different groups of
customers. Therefore the unit price must be computed per request, rather than being hard coded into
a database column.

.. _cookiecutter-django-shop: https://github.com/awesto/cookiecutter-django-shop
.. _Django model: https://docs.djangoproject.com/en/stable/topics/db/models/


.. _tutorial/product-model-i18n_smartcard:

An Internationalized Smart Card Model
=====================================

If in the demo provided by cookiecutter-django-shop_, support for multiple languages (I18N) is
enabled, the product model for our Smart Card changes slightly.

First ensure that django-parler_ is installed and ``'parler'`` is listed in the project's
``INSTALLED_APPS``. Then import some extra classes into the project's ``models.py`` and adopt the
product class. Only the relevant changes to our model class are shown here:

.. code-block:: python

	...
	from parler.managers import TranslatableManager, TranslatableQuerySet
	from polymorphic.query import PolymorphicQuerySet
	...

	class ProductQuerySet(TranslatableQuerySet, PolymorphicQuerySet):
	    pass

	class ProductManager(BaseProductManager, TranslatableManager):
	    queryset_class = ProductQuerySet

	    def get_queryset(self):
	        qs = self.queryset_class(self.model, using=self._db)
	        return qs.prefetch_related('translations')

	class SmartCard(CMSPageReferenceMixin, TranslatableModelMixin, BaseProduct):
	    ...
	    caption = TranslatedField()
	    description = TranslatedField()
	    ...

	class SmartCardTranslation(TranslatedFieldsModel):
	    master = models.ForeignKey(
	        SmartCard,
	        related_name='translations',
	        null=True,
	    )

	    caption = models.TextField(
	        "Caption",
	        help_text="Short description used in the catalog's list view.",
	    )

	    description = models.TextField(
	        "Description",
	        help_text="Long description used in the product's detail view.",
	    )

	    class Meta:
	        unique_together = [('language_code', 'master')]

For this model we decided to translate the fields ``caption`` and ``description``. The product name
of a Smart Card is international anyways and doesn't have to be translated into different langauges.
Hence we neither use a translatable field for the product name, nor its slug. On the other hand, if
it makes sense to translate the product name, then we'd simply move these fields into the related
class ``SmartCardTranslation``. This gives us all the flexibility we need to model our products
according to their physical properties, and prevents that the administrator of the site has to enter
redundant data through the administration backend, while creating or editing an instance.


Add Product Model to Django Admin
=================================

In order to make our Smart Card editable, we have to register it in the Django administration
backend:

.. code-block:: python

	from django.contrib import admin
	from adminsortable2.admin import SortableAdminMixin
	from shop.admin.product import CMSPageAsCategoryMixin, ProductImageInline, InvalidateProductCacheMixin
	from myshop.models import SmartCard

	@admin.register(SmartCard)
	class SmartCardAdmin(InvalidateProductCacheMixin, SortableAdminMixin, CMSPageAsCategoryMixin, admin.ModelAdmin):
	    fields = ['product_name', 'slug', 'product_code', 'unit_price', 'active', 'caption', 'description',
	              'storage', 'card_type']
	    inlines = [ProductImageInline]
	    prepopulated_fields = {'slug': ['product_name']}
	    list_display = ['product_name', 'product_code', 'unit_price', 'active']

This is a typical implementation of a Django ModelAdmin_. This class uses a few additions however:

* :class:`shop.admin.product.InvalidateProductCacheMixin`: After saving a product instance, all
  caches are going to be cleared.
* :class:`adminsortable2.admin.SortableAdminMixin`: Is used to add sorting capabilities to the
  backend list view.
* :class:`shop.admin.product.CMSPageAsCategoryMixin`: Is used to assign a product to one ore more
  CMS pages, tagged as Categories.
* :class:`shop.admin.product.ProductImageInline`: Is used to assign a one ore more images to a
  product and sort them accordingly.

.. _ModelAdmin: https://docs.djangoproject.com/en/stable/ref/contrib/admin/


With I18N support
-----------------

If multilingual support is required, then we also must add a possibility to make some fields
translatable:

.. code-block:: python

	from parler.admin import TranslatableAdmin
	...
	class SmartCardAdmin(InvalidateProductCacheMixin, SortableAdminMixin, TranslatableAdmin, CMSPageAsCategoryMixin, admin.ModelAdmin):
		...

For detail, please refer to the documentation provided by django-parler_.

.. _django-parler: https://django-parler.readthedocs.io/en/latest/


Next Chapter
============

In the next chapter of this tutorial, we will see how to organize the :ref:`tutorial/cart-checkout`
