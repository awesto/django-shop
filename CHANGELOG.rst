Version NEXT
============

* Fixed a problem, when the cart was transformed into an order using 
  OrderManager.create_from_cart
  Here instead of a free form state argument, the cart object itself
  has been passed to the CartModifier. This was inconsistent behavior.

Version 0.1.1
=============

* Changed CurrencyField default decimal precision back to 2

Version 0.1.0
=============

* Bumped the CurrencyField precision limitation to 30 max_digits and 10 decimal
  places, like it should have been since the beginning.
* Made Backends internationalizable, as well as the BillingShippingForm
  thanks to the introduciton of a new optional backend_verbose_name attribute
  to backends.
* Added order_required decorator to fix bug #84, which should be used on all 
  payment and shipping views
* Added cart_required decorator that checks for a cart on the checkout view #172
* Added get_product_reference method to Product (for extensibility)
* Cart object is not saved to database if it is empty (#147)
* Before adding items to cart you now have to use get_or_create_cart with save=True
* Changed spelling mistakes in methods from `payed` to `paid` on the Order 
  model and on the API. This is potentially not backwards compatible in some 
  border cases.
* Added a mixin class which helps to localize model fields of type DecimalField
  in Django admin view.
* Added this newly created mixin class to OrderAdmin, so that all price fields
  are handled with the correct localization.
* Order status is now directly modified in the shop API
* CartItem URLs were too greedy, they now match less.
* In case a user has two carts, one bound to the session and one to the user, 
  the one from the session will be used (#169)
* Fixed circular import errors by moving base models to shop.models_bases and 
  base managers to shop.models_bases.managers

Version 0.0.13
==============

(Version cleanup)

Version 0.0.12
==============

* Updated translations
* Split urls.py into several sub-files for better readability, and put in a
  urls shubfolder.
* Made templates extend a common base template
* Using a dynamically generated form for the cart now to validate user input.
  This will break your cart.html template. Please refer to the changes in 
  cart.html shipped by the shop to see how you can update your own template.
  Basically you need to iterate over a formset now instead of cart_items.
* Fixed a circular import problem when user overrode their own models

Version 0.0.11
==============

* Performance improvement (update CartItems are now cached to avoid unnecessary
  db queries)
* Various bugfixes


Version 0.0.10
==============

* New hooks were added to cart modifiers: pre_process_cart and
  post_process_cart.
* [API change] Cart modifiers cart item methods now recieve a state object,
  that allows them to pass information between cart modifiers cheaply.
* The cart items are not automatically saved after  process_cart_item anymore.
  This allows for cart modifiers that change the cart's content (also
  deleting).
* Changed the version definition mechanism. You can now: import shop;
  shop.__version__. Also, it now conforms to PEP 386
* [API Change] Changed the payment backend API to let get_finished_url 
  and get_cancel_url return strings instead of HttpResponse objects (this 
  was confusing)
* Tests for the shop are now runnable from any project
* added URL to CartItemView.delete()

Version 0.0.9
=============

* Changed the base class for Cart Modifiers. Methods are now expected to return
  a tuple, and not direectly append it to the extra_price_fields. Computation of
  the total is not done using an intermediate "current_total" attribute.
* Added a SHOP_FORCE_LOGIN setting that restricts the checkout process to
  loged-in users.

Version 0.0.8
=============

* Major change in the way injecting models for extensibility works: the base
  models are now abstract, and the shop provides a set of default implementations
  that users can replace / override using the settings, as usual. A special
  mechanism is required to make the Foreign keys to shop models work. This is
  explained in shop.utils.loaders

Version 0.0.7
=============

* Fixed bug in the extensibility section of CartItem
* Added complete German translations
* Added verbose names to the Address model in order to have shipping and 
  billing forms that has multilingual labels.

Version 0.0.6
=============

(Bugfix release)

* Various bugfixes
* Creating AddressModels for use with the checkout view (the default ones at
  least) were bugged, and would spawn new instances on form post, instead of
  updating the user's already existing ones.
* Removed redundant payment method field on the Order model.
* The "thank you" view does not crash anymore when it's refreshed. It now
  displays the last order the user placed.
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
