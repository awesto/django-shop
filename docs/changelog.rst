.. _changelog:

=========================
Changelog for django-SHOP
=========================


0.10.3
======
* Fix: :class:`shop.rest.renderers.CMSPageRenderer` always uses the template offered by the CMS page,
  rather than invoking method ``get_template_names()`` from the corresponding ``APIView`` class.
* Feature: Add class:`shop.rest.renderers.ShopTemplateHTMLRenderer` which is the counterpart of
  :class:`shop.rest.renderers.CMSPageRenderer`, usable for hardcoded Django views.
* Refactor: In examples *polymorphic* and *i18n_polymorphic*, renamed ``SmartPhone`` to ``SmartPhoneVariant``.
* Feature: In :class:`shop.money.fields.MoneyFormField` use a widget which renders the currency.
* Fix: Handle non-decimal types in :method:`shop.money.fields.MoneyField.get_db_prep_save`.
* Fix: In AngularJS, changes on filters and the search field did not work on Safari.
* Fix: In :method:`shop.views.auth.AuthFormsView.post` create a customer object from request for
  a visiting customers, rather than responding with *BAD REQUEST*.


0.10.2
======

* Fixed migration error in ``0004_ckeditor31.py``.
* Fixed #554: Email is no longer created when notification is triggered.
* Fixed: Using a ``ManyToManyField`` through ``ProductPage`` ignores the blank attribute,
  when saving a product in the admin backend.
* Hard code "Cart" into tooltip for cart icon, until https://github.com/divio/django-cms/issues/5930
  is fixed.
* Renders a nicer summary when rendering a multiple address form.
* Fixed: When placeholder is ``None`` raises AttributeError.


0.10.1
======

* Fixed #537 and #539: Rendering `data` in template has different results after upgrading to 0.10.


0.10.0
======

* In the backend, ``OrderAdmin`` and ``OrderItemAdmin`` may render the dictionary ``extra`` from
  their associated models using a special template.
* In ``OrderAdmin`` use methods ``get_fields()`` and ``get_readonly_fields()`` as intended.
* Tested with Django-1.10. Drop support for Django-1.8.
* If an anonymous customer logs in, his current cart is merged with a cart, which has previously
  been created. This has been adopted to re-use the method Product.is_in_cart()
  in and finds it's Merge the contents of the other cart into this one, afterwards delete it.
* Moved field ``salutation`` from :class:`shop.models.customer.BaseCustomer` into the merchant
  implementation. If your project does not use the provided default customer model
  :class:`shop.models.defaults.customer.Customer`, then you should add the ``salutation`` field
  to your implementation of the Customer model, if that makes sense in your use-case.
* Refactored the defaults settings for ``shop`` using an ``AppSettings`` object.
* Refactored all serializers into their own folder ``shop/serializers`` with submodules
  ``bases.py``, ``cart.py``, ``order.py`` and ``defaults.py``. The serializers
  ``CustomerSerializer``, ``ProductSummarySerializer`` and ``OrderItemSerializer`` now are
  configurable through the application settings.
* AngularJS directive ``<shop-auth-form ...>`` now listens of the event "pressed ENTER key"
  and submits the form data accordingly.
* Upgraded to AngularJS version 1.5.9.
* HTML5 mode is the default now.
* The previously required additional endpoint for the autocomplete search, can now be be merged
  into the same endpoint as connected to the catalog's list view. This has been made possible by
  the wrapper :class:`shop.search.views.CMSPageCatalogWrapper` which dispatch incoming requests
  to either the :class:`shop.views.catalog.ProductListView` or, for search queries to
  :class:`shop.search.views.SearchView`.
* Added choice option "Infinite Scroll" to the Cascade plugins **Catalog List View** and
  **Search Results**. They influence if the paginator is rendered or trigger an event to load
  more results from the server.
* Changed all Cascade plugins to follow the new API introduced in **djangocms-cascade** version 0.12.
* Directive ``shop-product-filter`` must be member of a ``<form ...>`` element.
* Unified the plugins **ShippingAddressFormPlugin** and **BillingAddressFormPlugin** into one plugin
  named **CheckoutAddressPlugin**, where the merchant can choose between the shipping- or billing
  form.
* Refactored :class:`shop.forms.checkout.AddressForm` and fixed minor bugs when editing multiple
  addresses.
* In address models, replaced ``CharField`` for ``country`` against a special ``CountryField``.
* Change value of ``BaseShippingAddress.address_type`` to ``shipping`` and
  ``BaseBillingAddress.address_type`` to ``billing``.
* Method ``shop.models.order.OrderManager.get_latest_url()`` falls back to
  ``reverse('shop-order-last')`` if no such page with ID ``shop-order-last`` was found in the CMS.
* Use menu_title instead of page title for link and tooltip content.
* In ``DialogForm``, field ``plugin_id`` is not required anymore.
* After a new customer recognized himself, the signal ``customer_recognized`` is fired so that
  other apps can act upon.
* Unified ``ProductCommonSerializer``, ``ProductSummarySerializer`` and ``ProductDetailSerializer``
  into a single ``ProductSerializer``, which acts as default for the ``ProductListView`` and
  ``ProductRetrieveView``.
* Dependency to **djangocms-cascade** is optional now.
* Added alternative compressor for ``{% render_block "js/css" "shop.sekizai_processors.compress" %}``
  which can handle JS/CSS files provided using ``{% addtoblock "js/css" ... %}`` even if located
  outside the ``/static/`` folders.
* Added method ``post_process_cart_item`` to the Cart Modifiers.
* In ``CartItem`` the ``product_code`` is mandatory now. It moves from being optionally kept in dict
  ``CartItem.extra`` into the ``CartItem`` model itself. This simplifies a lot of boilerplate code,
  otherwise required by the merchant implementation. Please read :ref:`upgrading-0.10` for details.
* In :class:`shop.models.product.BaseProduct` added a hook method ``get_product_variant(self, **kwargs)``
  which can be overridden by products with variations to return a product variant.


0.9.3
=====
* Added template context processor :func:`shop.context_processors.ng_model_options` to add the
  settings ``EDITCART_NG_MODEL_OPTIONS`` and ``ADD2CART_NG_MODEL_OPTIONS``. Please check your
  templates to see, if you still use ``ng_model_options``.
* Allows to add children to the ``CartPlugin``. These children are added to the table foot of the
  rendered cart.
* Added AngularJS directive ``<ANY shop-forms-set>`` which can be used as a wrapper, when the
  proceed button shall be added to a page containing ``<form ...>`` elements with built in
  validation.
* All Cascade plugins use ``GlossaryField`` instead of a list of ``PartialFormField`` s. This is
  much more "Djangonic", but requires djangocms-cascade version 0.11 or later.
* All urlpatterns are compatible with configurations adding a final / to the request URL.
* The URL for accessing an Order object, now uses the order number instead of it's primary key.


0.9.2
=====

* Minimum required version of django-filer is now 1.2.5.
* Minimum required version of djangocms-cascade is now 0.10.2.
* Minimum required version of djangoshop-stripe is now 0.2.0.
* Changed the default address models to be more generic. Please read the
  :doc:`upgrade instructions <upgrading>` if you are upgrading from 0.9.0 or 0.9.1.
* Fixed :py:meth:`shop.money.fields.decontruct` to avoid repetitive useless generation of migration
  files.
* Using cached_property decoration for methods ``unit_price`` and ``line_total`` in
  :class:`shop.models.order.OrderItem`.
* Fixed #333: Accessing the cart when there is no cart associated with a customer.
* Removed Apphook :class:`shop.cms_apps.OrderApp`. This class now must be added to the project's
  ``cms_apps.py``. This allows the merchant to override the
  :class:`shop.rest.serializers.OrderListSerializer` and :class:`shop.rest.serializers.OrderDetailSerializer`.
* Bugfix: declared django-rest-auth as requirement in setup.py.
* Refactored shop.models.deferred -> shop.deferred. This allows to add a check for pending mappings
  into the ready-method of the shop's AppConfig.
* Prepared for Django-1.10: Replaced all occurrences of :py:meth:`django.conf.urls.patterns` by
  a simple list.
* Method ``get_render_context`` in classes extending from ``django_filters.FilterSet`` now must be a
  ``classmethod`` accepting a request object and the querystring.
* Method ``get_renderer_context`` in class ``CMSPageProductListView`` now fetches the rendering
  context for filtering *after* the queryset have been determined. This allows us to adopt the
  context.
* Function ``loadMore()`` in ``CatalogListController`` bypasses the existing search query. This
  allows to use hard coded links for tag search.
* Using Python's ``Enum`` class to declare customer states, such as UNRECOGNIZED, GUEST or
  REGISTERED.
* Created a customized database field to hold the customers states, as stored by the above
  ``Enum``.
* Fixed: A server-side invalidated email addresses was accepted anyway, causing problems for
  returning customers.
* Renamed CMS Page IDs for better consistency:
  * ``personal-details`` -> ``shop-customer-details`` to access the Customer Detail Page.
  * ``reset-password`` -> ``shop-password-reset`` to access the Reset Password Page.
  * new: ``shop-register-customer`` to access the Register User Page.
* Moved all non-Python dependencies from ``bower_components`` into ``node_modules``.
* The breadcrumb now is responsible itself for being wrapped into a Bootstrap container.
* Use Sekizai processors from django-angular. Replaced ``shop-ng-requires`` against ``ng-requires``
  and ``shop-ng-config`` against ``ng-config``.

0.9.1
=====

* Support for Python 3
* Support for Django-1.9
* Added abstract classes class:`shop.models.delivery.BaseDelivery` and class:`shop.models.delivery.BaseDeliveryItem`
  for optional partial shipping.


0.9.0
=====

* Separated class:`shop.views.catalog.ProductListView` into its base and the new class
  class:`shop.views.catalog.CMSPageProductListView` which already has added it appropriate
  filters.
* Moved ``wsgi.py`` into upper folder.
* Prototype of :class:`shop.cascade.DialogFormPluginBase.get_form_data` changed. It now accepts
  ``context``, ``instance`` and ``placeholder``.
* Fixed: It was impossible to enter the credit card information for Stripe and then proceed to the
  next step. Using Stripe was possible only on the last step. This restriction has gone.
* It now also is possible to display a summary of your order before proceeding to the final
  purchasing step.
* To be more Pythonic, class:`shop.models.cart.CartModelManager` raises a ``DoesNotExist`` exception
  instead of ``None`` for visiting customers.
* Added method ``filter_from_request`` to class:`shop.models.order.OrderManager`.
* Fixed: OrderAdmin doesn't ignores error if customer URL can't be resolved.
* Fixed: Version checking of Django.
* Fixed: Fieldsets duplication in Product Admin.
* CartPlugin now can be child of ProcessStepPlugin and BootstrapPanelPlugin.
* Added ShopAddToCartPlugin.
* All Checkout Forms now can be rendered as editable or summary.
* All Dialog Forms now can declare a legend.
* In ``DialogFormPlugin``, method ``form_factory`` always returns a form class instead of an error
  dict if form was invalid.
* Added method ``OrderManager.filter_from_request``, which behaves analogous to
  ``CartManager.get_from_request``.
* Fixed lookups using MoneyField by adding method get_prep_value.
* Dropped support for South migrations.
* Fixed: In ``ProductIndex``, translations now are always overridden.
* Added class ``SyncCatalogView`` which can be used to synchronize the cart with a catalog list
  view.
* Content of Checkout Forms is handled by a single transaction.
* All models such as Product, Order, OrderItem, Cart, CartItem can be overridden by the merchant's
  implementation. However, we are using the deferred pattern, instead of configuration settings.
* Categories must be implemented as separate **django-SHOP** addons. However for many
  implementations pages form the **django-CMS** can be used as catalog list views.
* The principle on how cart modifiers work, didn't change. There more inversion of control now, in
  that sense, that now the modifiers decide themselves, how to change the subtotal and final total.
* Existing Payment Providers can be integrated without much hassle.


Since version 0.2.1 a lot of things have changed. Here is a short summary:
==========================================================================

* The API of **django-SHOP** is accessible through a REST interface. This allows us to build MVC on
  top of that.

* Changed the two OneToOne relations from model Address to User, one was used for shipping, one for
  billing. Now abstract BaseAddress refers to the User by a single ForeignKey giving the ability to
  link more than one address to each user. Additionally each address has a priority field for
  shipping and invoices, so that the latest used address is offered to the client.

* Replaced model shop.models.User by the configuration directive ``settings.AUTH_USER_MODEL``, to be
  compliant with Django documentation.

* The cart now is always stored inside the database; there is no more distinction between session
  based carts and database carts. Carts for anonymous users are retrieved using the visitor's
  session_key. Therefore we don't need a utility function such ``get_or_create_cart`` anymore.
  Everything is handled by the a new CartManager, which retrieves or creates or cart based on
  the request session.

* If the quantity of a cart item drops to zero, this items is not automatically removed from the
  cart. There are plenty of reasons, why it can make sense to have a quantity of zero.

* A WatchList (some say wish-list) has been added. This simply reuses the existing Cart model,
  where the item quantity is zero.

* Currency and CurrencyField are replaced by Money and MoneyField. These types not only store the
  amount, but also in which currency this amount is. This has many advantages:

  * An amount is rendered with its currency symbol as a string. This also applies for JSON
    data-structures, rendered by the REST framework.

  * Money types of different currencies can not be added/substracted by
    accident.  Normal installations woun't be affected, since each shop system
    must specify its default currency.

* Backend pools for Payment and Shipping have been removed. Instead, a Cart Modifier can inherit
  from :class:`PaymentModifier` or :class:`ShippingModifier`. This allows to reuse the Cart Modifier
  Pool for these backends and use the modifiers logic for adding extra rows to he carts total.

* The models :class:`OrderExtraRow` and :class:`OrderItemExtraRow` has been replaced by a JSONField
  extra_rows in model :class:`OrderModel` and :class:`OrderItemModel`. :class:`OrderAnnotation` now
  also is stored inside this extra field.

* Renamed for convention with other Django application:

  * date_created -> created_at
  * last_updated -> updated_at
  * ExtraOrderPriceField -> BaseOrderExtraRow
  * ExtraOrderItemPriceField -> BaseItemExtraRow


Version 0.2.1
=============
This is the last release on the old code base. It has been tagged as 0.2.1 and can be examined for
historical reasons. Bugs will not be fixed in this release.


Version 0.2.0
=============
* models.FloatField are now automatically localized.
* Support for Django 1.2 and Django 1.3 dropped.
* Product model now has property ``can_be_added_to_cart`` which is checked before adding the product to cart
* In cart_modifiers methods ``get_extra_cart_price_field`` and ``get_extra_cart_item_price_field``
  accepts the additional object ``request`` which can be used to calculate the price
  according to the state of a session, the IP-address or whatever might be useful.
  Note for backwards compatibility: Until version 0.1.2, instead of the ``request``
  object, an empty Python dictionary named ``state`` was passed into the cart
  modifiers. This ``state`` object could contain arbitrary data to exchange information
  between the cart modifiers. This Python dict now is a temporary attribute of the
  ``request`` object named ``cart_modifier_state``. Use it instead of the
  ``state`` object.
* Cart modifiers can add an optional ``data`` field beside ``label`` and ``value``
  for both, the ExtraOrderPriceField and the ExtraOrderItemPriceField model.
  This extra ``data`` field can contain anything serializable as JSON.

Version 0.1.2
=============

* cart_required and order_required decorators now accept a reversible url
  name instead and redirect to cart by default
* Added setting `SHOP_PRICE_FORMAT` used in the `priceformat` filter
* Separation of Concern in OrderManager.create_from_cart:
  It now is easier to extend the Order class with customized
  data.
* Added OrderConfirmView after the shipping backend views that can be easily
  extended to display a confirmation page
* Added example payment backend to the example shop
* Added example OrderConfirmView to the example shop
* Unconfirmed orders are now deleted from the database automatically
* Refactored order status (requires data migration)
    * removed PAYMENT and added CONFIRMING status
    * assignment of statuses is now linear
    * moved cart.empty() to the PaymentAPI
    * orders now store the pk of the originating cart
* Checkout process works like this:
    1. CartDetails
    2. CheckoutSelectionView
        * POST --> Order.objects.create_from_cart(cart) removes all orders originating from this cart that have status < CONFIRMED(30)
        * creates a new Order with status PROCESSING(10)
    3. ShippingBackend
        * self.finished() sets the status to CONFIRMING(20)
    4. OrderConfirmView
        * self.confirm_order() sets the status to CONFIRMED(30)
    5. PaymentBackend
        * self.confirm_payment() sets the status to COMPLETED(40)
        * empties the related cart
    6. ThankYouView
        * does nothing!

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
