.. _reference/product-models:

==============
Product Models
==============

Products can vary wildly, and modeling them is not always trivial. Some products are salable in
pieces, while others are continues. Trying to define a set of product models, capable for describing
all such scenarios is impossible –


Describe Products by customizing the Model
==========================================

**DjangoSHOP** requires to describe products instead of prescribing prefabricated models.

All in all, the merchant always knows best how to describe his products!


E-commerce solutions, claiming to be plug-and-play, usually use one of these (anti-)patterns
--------------------------------------------------------------------------------------------

Either, they offer a field for every possible variation, or they use the `Entity Attribute Value`_
(EAV) pattern to add meta-data for each of our models. This at a first glance seems to be easy.
But both approaches are unwieldy and have serious drawbacks. They both apply a different "physical
schema" – the way data is stored, rather than a "logical schema" – the way users and applications
require that data. As soon as we have to combine our e-commerce solution with some
Enterprise Resource Planning (ERP) software, additional back-and-forward conversion routines have
to be added.

.. _Entity Attribute Value: https://en.wikipedia.org/wiki/Entity%E2%80%93attribute%E2%80%93value_model


In **django-SHOP**, the physical representation of a product always maps to its logical
---------------------------------------------------------------------------------------

**Django-SHOP**'s approach to this problem is to have a minimal set of models. These abstract models
are stubs providing to subclass the physical models. Hence the logical representation of the
product conforms to their physical one. Moreover, it is even possible to represent various types of
products by subclassing polymorphically from an abstract base model. Thanks to Django's Object
Relational Mapper, modeling the logical representation for a set of products, together with an
administration backend, becomes almost effortless.

Therefore the base class to model a product is a stub which contains only these three fields:

The timestamps for ``created_at`` and ``updated_at``; these are self-explanatory.

A boolean field ``active``, used to signalize the products availability.

The attentive reader may wonder, why there not even fields for the most basic requirements of each
sellable article, there is no product name, no price field and no product code.

The reason for this is, that **django-SHOP** does not impose any fields, which might require
a different implementation for the merchants use case. However, for a sellable commodity some
information is fundamental and required. But its up to him how to implement these fields:

The product's name must be implemented as a model field or as a property method, but both must be
declared as ``product_name``. Use a method implementation for composed and translatable names,
otherwise use a database model field with that name.

The product's price must be implemented as a method declared as ``get_price(request)`` which accepts
the request object. This gives the merchant the ability to vary the price and/or its currency
depending on the geographic location, the customers login status, the browsers user-agent, or
whatever else.

An optional, but highly recommended field is the products item number, declared as
``product_code``. It shall return a unique and language independent identifier for each product,
to be identifiable. In most cases the product code is implemented by the product model itself, but
in some circumstances it may be implemented by the product's variant. The product model
``SmartPhone``, as referenced in the demo code, is one such example.

The example section of **django-SHOP** contains a few models which can be copied and adopted to the
specific needs of the merchants products. Let's have a look at a few use-cases:


Case study: Smart-Phones
========================

There are many smart-phone models with different equipment. All the features are the same, except
for the built-in storage. How shall we describe such a model?

In that model, the product's name shall not be translatable, not even on a multi-lingual site, since
smart-phones have international names used everywhere. Smart-phones models have dimensions, an
operating system, a display type and other features.

But smart-phone have different equipment, namely the built-in storage, and depending on that, they
have different prices and a unique product code. Therefore our product models consists of two
classes, the generic smart phone model and the concrete flavor of that model.

Therefore we would model our smart-phones using a database model similar to the following one:

.. code-block:: python

	from shop.models.product import BaseProductManager, BaseProduct
	from shop.money import Money

	class SmartPhoneModel(BaseProduct):
	    product_name = models.CharField(
	        _("Product Name"),
	        max_length=255,
	    )

	    slug = models.SlugField(_("Slug"))

	    description = HTMLField(
	        help_text=_("Detailed description."),
	    )

	    manufacturer = models.ForeignKey(
	        Manufacturer,
	        verbose_name=_("Manufacturer"),
	    )

	    screen_size = models.DecimalField(
	        _("Screen size"),
	        max_digits=4,
	        decimal_places=2,
	    )
	    # other fields to map the specification sheet

	    objects = BaseProductManager()

	    lookup_fields = ('product_name__icontains',)

	    def get_price(request):
	        aggregate = self.variants.aggregate(models.Min('unit_price'))
	        return Money(aggregate['unit_price__min'])

	class SmartPhoneVariant(models.Model):
	    product_model = models.ForeignKey(
	        SmartPhoneModel,
	        related_name='variants',
	    )

	    product_code = models.CharField(
	        _("Product code"),
	        max_length=255,
	        unique=True,
	    )

	    unit_price = MoneyField(_("Unit price"))

	    storage = models.PositiveIntegerField(_("Internal Storage"))

Lets go into the details of these classes. The model fields are self-explanatory. Something to note
here is, that each product requires a field ``product_name``. This alternatively can also be
implemented as a translatable field using django-parler_, see below.

Another mandatory attribute for each product is the ``ProductManager`` class. It must inherit
from ``BaseProductManager``, and adds some methods to generate special querysets.

Finally, the attribute ``lookup_fields`` contains a list or tuple of `lookup fields`_. These are
required by the administration backend, and used when the site editor has to search for certain
products. Since the framework does not impose which fields are used to distinguish between products,
we must give a hint here.

Each product also requires a method implemented as ``get_price(request)``. This must return the
unit price using one of the available :ref:`reference/money-types`.


Add multilingual support
------------------------

Adding multilingual support to an existing product is quite easy and straight forward. To achieve
this **django-SHOP** uses the app django-parler_ which provides Django model translations without
nasty hacks. All we have to do, is to replace the ProductManager with one capable of handling
translations:

.. code-block:: python

	class ProductQuerySet(TranslatableQuerySet, PolymorphicQuerySet):
	    pass

	class ProductManager(BaseProductManager, TranslatableManager):
	    queryset_class = ProductQuerySet

The next step is to locate the model fields, which shall be available in different languages. In
our use-case thats only the product's description:

.. code-block:: python

	class SmartPhoneModel(BaseProduct, TranslatableModel):
	    # other field remain unchanged
	    description = TranslatedField()

	class ProductTranslation(TranslatedFieldsModel):
	    master = models.ForeignKey(
	        SmartPhoneModel,
	        related_name='translations',
	        null=True,
	    )

	    description = HTMLField(
	        help_text=_("Some more detailed description."),
	    )

	    class Meta:
	        unique_together = [('language_code', 'master')]

This simple change now allows us to offer the shop's assortment in different natural languages.

.. _lookup fields: https://docs.djangoproject.com/en/stable/topics/db/queries/#complex-lookups-with-q-objects
.. _django-parler: http://django-parler.readthedocs.org/


Add Polymorphic Support
-----------------------

If besides smart phones we also want to sell cables, pipes or smart cards, we must split our product
models into a common- and a specialized part. That said, we must separate the information every
product requires from the information specific to a certain product type. Say, in addition to smart
phones, we also want to sell smart cards. First we declare a generic ``Product`` model, which is a
common base class of both, ``SmartPhone`` and ``SmartCard``:

.. code-block:: python

	class Product(BaseProduct, TranslatableModel):
	    product_name = models.CharField(
	        _("Product Name"),
	        max_length=255,
	    )

	    slug = models.SlugField(
	        _("Slug"),
	        unique=True,
	    )

	    description = TranslatedField()

	    objects = ProductManager()
	    lookup_fields = ['product_name__icontains']

Next we only add the product specific attributes to the class models derived from ``Product``:

.. code-block:: python

	class SmartPhoneModel(Product):
	    manufacturer = models.ForeignKey(
	        Manufacturer,
	        verbose_name=_("Manufacturer"),
	    )

	    screen_size = models.DecimalField(
	        _("Screen size"),
	        max_digits=4,
	        decimal_places=2,
	    )

	    battery_type = models.PositiveSmallIntegerField(
	        _("Battery type"),
	        choices=BATTERY_TYPES,
	    )

	    battery_capacity = models.PositiveIntegerField(
	        help_text=_("Battery capacity in mAh"),
	    )

	    ram_storage = models.PositiveIntegerField(
	        help_text=_("RAM storage in MB"),
	    )
	    # and many more attributes as found on the data sheet

	class SmartPhone(models.Model):
	    product_model = models.ForeignKey(SmartPhoneModel)
	    product_code = models.CharField(
	        _("Product code"),
	        max_length=255,
	        unique=True,
	    )

	    unit_price = MoneyField(_("Unit price"))

	    storage = models.PositiveIntegerField(_("Internal Storage"))

	class SmartCard(Product):
	    product_code = models.CharField(
	        _("Product code"),
	        max_length=255,
	        unique=True,
	    )

	    storage = models.PositiveIntegerField(help_text=_("Storage capacity in GB"))

	    unit_price = MoneyField(_("Unit price"))

	    CARD_TYPE = [2 * ('{}{}'.format(s, t),)
	                 for t in ('SD', 'SDXC', 'SDHC', 'SDHC II') for s in ('', 'micro ')]
	    card_type = models.CharField(
	        _("Card Type"),
	        choices=CARD_TYPE,
	        max_length=15,
	    )

	    SPEED = [(str(s), "{} MB/s".format(s))
	             for s in (4, 20, 30, 40, 48, 80, 95, 280)]
	    speed = models.CharField(
	        _("Transfer Speed"),
	        choices=SPEED,
	        max_length=8,
	    )

If *MyShop* would sell the iPhone5 with 16GB and 32GB storage as independent products, then we could
unify the classes ``SmartPhoneModel`` and ``SmartPhone`` and move the attributes ``product_code``
and ``unit_price`` into the class ``Product``. This would simplify some programming aspects, but
would require the merchant to add a lot of information twice. Therefore we remain with the
model layout presented here.


Caveat using a ``ManyToManyField`` with existing models
=======================================================

Sometimes we may need to use a ``ManyToManyField`` for models which are handled by other apps in
our project. This for example could be an attribute ``files`` referring the model
``filer.FilerFileField`` from the library django-filer_. Here Django would try to create a mapping
table, where the foreign key to our product model can not be resolved properly, because while
bootstrapping the application, our Product model is still considered to be deferred.

Therefore, we have to create our own mapping model and refer to it using the ``through``
parameter, as shown in this example:

.. code-block:: python

	from six import with_metaclass
	from django.db import models
	from filer.fields.file import FilerFileField
	from shop.models import deferred
	from shop.models.product import BaseProductManager, BaseProduct

	class ProductFile(with_metaclass(deferred.ForeignKeyBuilder, models.Model)):
	    file = FilerFileField()
	    product = deferred.ForeignKey(BaseProduct)

	class Product(BaseProduct):
	    # other fields
	    files = models.ManyToManyField('filer.File', through=ProductFile)

	    objects = ProductManager()

.. note:: Do not use this example for creating a many-to-many field to ``FilerImageField``.
	Instead use :class:`shop.models.related.BaseProductImage` which is a base class for this kind
	of mapping. Just import and materialize it, in your own project.

.. _django-filer: https://github.com/divio/django-filer
