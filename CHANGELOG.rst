Version 0.0.6
=============

* Fixed a bug in the shippingbilling view where the returned form was a from
  class instead of a from instance.

Version 0.0.5
=============

* Fix a bug in 0.0.4 that made South migration fail with Django < 1.3

Version 0.0.4
=============

* Addresses are now stored as one single text field on the Order objects
* OrderItems now have a ForeignKey relation to Products (to retrieve the
  product more easily)
* New templatetag ("products")
* Made most models swappable using settings (see docs)
* Changed checkout views. The shop uses one single checkout view by default now.
* Created new mechanism to use custom Address models (see docs)
* Moved all Address-related models to shop.addressmodel sub-app
* Removed Client Class
* Removed Product.long_description and Product.short_description from the
  Product superclass
* Bugfixes, docs update

Version 0.0.3
=============

* More packaging fixes (missing templates, basically)

Version 0.0.2
=============

* Packaging fix (added MANIFEST.in)

Version 0.0.1
=============

* Initial release to Pypi
