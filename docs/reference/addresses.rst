.. _reference/addresses:

==========================
Designing an Address Model
==========================

Depending on the merchant's needs, the business model and the catchment area of the site, the used
address models may vary widely. Since **djangoSHOP** allows to override almost every database model,
addresses are no exception here. The class :class:`shop.models.address.BaseAddress` only contains
a foreign key to the Customer model and a priority field used to sort multiple addresses by
relevance.

All the fields which make up an address, such as the addresse, the street, zip code, etc. are part
of the concrete model implementing an address. It is the merchant's responsibility to define which
address fields are required.


.. note:: unfinished document
