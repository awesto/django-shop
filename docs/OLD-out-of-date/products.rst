
.. _products:

========
Products
========

Handling a large number of different products can be a headache, since most products have very different properties
from one another (think amazon and the plethora of differnet stuff they sell).

A core product model should be extensible to the shop needs.
Different ways may exist for differnt use-cases:

* Use model inheritance::

     class MySpecialProduct(Product):
         """
         Adds special attributes etc.
         """

  This would mean that a product is e.g. a DVD or a Vegetable, but
  never both. Although on database level this would be perfectly
  possible.

* Use a kind of attachment approach::

     class MySpecialProductExtension(models.Model):
         """
         Adds special attributes and contains a relation to
         the core Product.
         """

         product = models.ForeignKey(Product)

  This way a product could get multiple different attachments to
  it. On database level this will be the same as using model
  inheritance. On python code level this has a different meaning (I
  think).

* Use the attributes approach for user-added custom attributes. See
  snippets/products.py for this approach.


The core Product model should not need to know anything about these
extensions. Django ORM will take care of reverse accessors to these
extensions.

Other Django-based webshops handle the complexity in a clever way: make the core product very extensible with so-called
product attributes. Similar to key-value tags, product attributes allow for very flexible product creation, and a clever
set of model managers hide the complexity of theses added tables quite well.

Are there reasons why these attributes should relate to Product
instead of implementing a generic attribute app? Maybe this way::

   class Attribute(models.Model):
       # relation stuff
       content_type = models.ForeignKey(ContentType)
       object_id = models.PositiveIntegerField()
       content_object = generic.GenericForeignKey('content_type', 'object_id')

       # content and type
       value = models.CharField(max_length = 500)
       description = models.TextField()
       type = models.ForeignKey(AttributeType)


See snippets/products.py for more info.
