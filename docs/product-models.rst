=========================================================
Describe your products through customized database models
=========================================================

djangoSHOP requires to describe your products instead of prescribing prefabricated models
=========================================================================================

Products can vary wildly, and modeling them is not always trivial. Some products are salable in
pieces, while others are continues. Trying to define a set of product models, capable for describing
all such scenarios is impossible – describe your product by customizing the model and not vice
versa.


E-commerce solutions, claiming to be plug-and-play, usually use one of these (anti-)patterns
---------------------------------------------------------------------------------------------

Either, they offer a field for every possible variation, or they use the Entity-Attribute-Value
pattern to add meta-data for each of your models. This at a first glance seems to be easy. But both
approaches are unwieldy and have serious drawbacks. They both apply a different "physical schema" –
the way data is stored, rather than a "logical schema" – the way users and applications require that
data. As soon as you have to combine your e-commerce solution with some Enterprise-Resource-Planning
software, additional back-and-forward conversion routines have to be added.


In djangoSHOP, the physical representation of a product corresponds to its logical
----------------------------------------------------------------------------------

**djangoSHOP**'s approach to this problem is to have minimal set of models. These abstract models
are stubs provided to subclass the physical models. Hence the logical representation of the
product conforms to their physical one. Moreover, it is even possible to represent various types of
products by subclassing polymorphically from an abstract base model. Thanks to Django's Object
Relational Mapper, modeling the logical representation for a set of products, together with an
administration backend, becomes almost effortless. 

Therefore the base class to model a product is a stub which contains only these three fields:

The timestamps for ``created_at`` and ``updated_at``. A boolean field ``active``, used to signalize
the products availability.

The savvy ready may wonder, why there not even fields for the most basic requirements of a
sellable article, there is no product name, no price field and no product code.

The reason for this is, that these fields have been implemented as methods to be overridden by
the concrete class implementing the product. The name for instance could be translatable using
the application django-parler_. The price could depend upon the geographic position of the
requesting browser and the product's code can depend on some kind of variations.

Therefore these fundamental fields have to be implemented by the merchant's class describing the
product. Since not even the most generic product model can describe the simplest commodity
appropriately, the authors of **djangoSHOP** have decided to ship it without any default model.

However, the example section contains a few models which can be copied and adopted to the specific
needs of the merchants products. Let's see a few use-cases:


Use-Case One: Smart-Phones
..........................

There are many smart-phone models with different equipment. All the features are the same, except
the built-in storage. Now, how shall we describe such a model?

The is a class for the smart-phone model. In that model, the product's name shall not be
translatable, not even on a multi-lingual site, since smart-phones have international names used
everywhere. Smart-phones models have dimensions, an operating system, a display type and other
features.

But smart-phone have different equipment, namely the built-in storage, and depending on that, they
have a price and a unique product code.

Therefore we would model our smart-phones using a similar database model:

.. code-block:: python

	from myshop.models.product import Product  # this model is explained later
	
	class SmartPhoneModel(Product):
	    manufacturer = models.ForeignKey(Manufacturer, verbose_name=_("Manufacturer"))
	    battery_capacity = models.PositiveIntegerField(_("Capacity"),
	        help_text=_("Battery capacity in mAh"))
	    operating_system = models.ForeignKey(OperatingSystem, verbose_name=_("Operating System"))
	    width = models.DecimalField(_("Width"), max_digits=4, decimal_places=1)
	    height = models.DecimalField(_("Height"), max_digits=4, decimal_places=1)
	    weight = models.DecimalField(_("Weight"), max_digits=5, decimal_places=1)
	    screen_size = models.DecimalField(_("Screen size"), max_digits=4, decimal_places=2)

	class SmartPhone(models.Model):
	    product_model = models.ForeignKey(SmartPhoneModel, verbose_name=_("Smart-Phone Model"))
	    product_code = models.CharField(_("Product code"), max_length=255, unique=True)
	    unit_price = MoneyField(_("Unit price"), decimal_places=3)
	    storage = models.PositiveIntegerField(_("Internal Storage"))
