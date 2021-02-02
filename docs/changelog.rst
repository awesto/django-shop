.. _changelog:

=========================
Changelog for django-SHOP
=========================

1.2.4
=====
* Fix setup.py to proper versionsioning.


1.2.3
=====
* Fix API change in library ``ipware`` version 3: Replace ``get_ip`` against ``get_client_ip``.


1.2.2
=====
* Fix #786: Make shipping costs disappear, if cart modifiers doesn't apply them anymore.
* Remove deprecated HTML tag ``<center>`` from email template used to render the order.
* Add Bolivian Boliviano to the list of currencies.
* Fix #819: Accessing customerproxy addresses in admin raises Type error.


1.2.1
=====
* In management command, make mandatory CMS page for rendering search results, recommended only.


1.2
===
* Add support for Django-3.0.
* For full-text searching, replace Haystack against elasticsearch-dsl.
* Drop support for Python 2.7 and 3.4.
* Drop support for Django-1.11 and 2.0.


1.1.4
=====
* Fix rendering bug in Product Gallery plugin.


1.1.3
=====
* Add South African Rand to currencies.


1.1.2
=====
* Fix #802: ``CartItemSerializer`` raised an exception if field ``CartItem.extra`` was handled by
  Django's internal Postgres ``JSONField``.
* Fix: In Django>2, rendering of OrderItem in Inline Admin did not work anymore.


1.1.1
=====
* Fix: Rendering text for full text index raised an exception.
* Upgrade calls to djangorestframework API to support version 3.9 and later.
* Fix: Generating email during purchansing operation raised an exception.


1.1
===

* Add support for Django-2.2, 2.1. Drop support for Django<1.11.
* Add wrapper around Django's messages framework so that messages can be displayed asynchronously
  using a new AngularJS directive ``<toast-messages>``.
* Add endpoint ``fetch_messages`` to fetch JSON description for toast-messages.
* Add stock managment offering a simple addon to products, or alternatively an inventory management
  class, allowing to sell short and limiting to special periods.
* Refactored views for adding product to cart and changing quantity in cart so that the purchasing
  quantity can not exceed the quantity in stock.
* The default commodity product now keeps track of the quantity in stock.
* Changed the signature of the methods :meth:`shop.modifiers.base.CartModifierBase.pre_process_cart`
  and :meth:`shop.modifiers.base.CartModifierBase.pre_process_cart_item` to take an extra boolean
  parameter.
* Remove sub-serializer ``availability`` from product, because now it is handled internally by the
  class :class:`shop.serializers.defaults.catalog.AddToCartSerializer`.
* For products with managed availability, show the remaining number in stock.
* Changed the field type of ``quantity`` in :class:`shop.models.defaults.cart_item.CartItem` and
  :class:`shop.models.defaults.order_item.OrderItem` from ``IntegerField`` to ``PositiveIntegerField``.
  (Ann.: This change, by accident slipped into version 1.0.1 and was reverted in 1.0.2).


1.0.2
=====
* Revert the change of the ``quantity`` field to use a ``PositiveIntegerField`` in the default
  implementations of ``CartItem`` and ``OrderItem`` models. This caused #766.
  This change was scheduled for version 1.1 but unfortunately slipped into version 1.0.1.


1.0.1
=====

* Fix error in admin interface for ``Notification`` detail view.
* Refactor all internal model checks to use classmethod ``check()`` provided by Django.


1.0
===

* Replace various files containing Python requirements against ``Pipfile`` to be used by pipenv_.
* Migrated all default templates to use Bootstrap-4 and replace all tables using the HTML tag
  ``<table>`` against flex elements.
* Switch to py.test_ in favor of Django test-cases.
* It now is possible to override the forms for selecting the payment-, shipping- and extra
  annotation using a configuration directive.
* Adopted to django-CMS version 3.5.
* Fix all compatibility issues with Django-1.11.
* Fix all compatibility issues with Django REST framework 3.8.
* Upgrade to angular-ui-bootstrap version 2.5. This requires djangocms-cascade version 0.17.x and a
  slight modification of the navbar rendering.
* Add Order number to Order List View.
* It is possible to access the Order Detail View anonymously by using a secret in the URL.
* Remove directory ``example`` in favor of the new project cookiecutter-django-shop_.
* Customized Template Engine which keeps track on referenced images and stores then as attachments
  to be used in multipart email messages. This requires a patched version of django-post_office_.
* Add ``relatated_name`` to fields ``delivery`` and ``item`` to the model ``Delivery``. Check your
  reverse relations.
* Added an apphook ``PasswordResetApp``, so that all pages, even those to reset the password, can
  now be handled by a page by the CMS.
* Pagination of catalog list view can distinguish between *auto-infinte*, *manual-infinte* and
  *pagination*.
* Pagination of catalog list view prevents widow items.
* Cart widget displays a short summary of products after adding a product, or mouse-over event.
* AddToCart now optionally renders a modal dialog after adding the product.
* All forms in the checkout process can be overridden using a settings variable.
* Buttons are configurable to be disabled, if wrapping form is invalid.
* Unified all management commands into ``shop`` with different subcommands.
* Add management command ``shop check-pages`` to verify mandatory and recommended CMS pages.
* Add management command ``shop review-settings`` to verify the configuration settings.
* Refactored payment- and shipping-modifiers into their own submodules, so that they stay
  side-by-side with their order workflow mixins.
* All payment- and shipping-modifiers support an instantiation either as list or as instance. This
  allows to implement payment- or shipping-service-provider offering different payment- or shipping
  methods themselves.
* Changed all relative import against absolute ones.
* In context for email template rendering, renamed ``data`` to a more meaningful name such as
  ``order``.
* Add support for inlined images when sending HTML emails.
* Replace FSM signal ``post_transition`` against a function ``transition_change_notification`` which
  either is invoked by ``OrderAdmin.save_model()`` or while processing an Order through the frontend
  by the customer.
* In Order event notification, add data about each delivery to the serialized Order data.
* Upgrade to djangocms-bootstrap version 1.0.2.
* Fix: Do not always refetch cart data from server.
* Improve style of rendering for invoice and delivery notes in the Order backend.
* Use specific naming for relatation of model ``DeliveryItem`` to models ``OrderItem`` and
  ``Delivery``.
* Add reusable scroll-spy for AngularJS directive ``navbar``.

.. _pipenv: https://pipenv.readthedocs.io/en/latest/
.. _py.test: https://docs.pytest.org/en/latest/
.. _cookiecutter-django-shop: https://github.com/awesto/cookiecutter-django-shop
.. _django-post_office: https://github.com/jrief/django-post_office/tree/attachments-allowing-MIMEBase

0.12.2
======
* Fix #729: Issue with Notification admin transition choices (RETURN_VALUE).
* Adopted templates to be used by **angular-ui-bootstrap** version 2.5.
* Compatible with **django-CMS** version 3.5.


0.12.1
======

* Fix: #724: broken amount rendering when ``USE_TOUSAND_SEPARATOR`` is ``True``.
* Adopt ``shoplinkplugin.js`` to use function ``initializeLinkTypes`` as required by
  **djangocms-cascade** version 0.16.


0.13
====

* Drop support for Django-1.9, add support for Django-1.11.
* Add method ``get_weight()`` to product model, so that a cart modifier may sum up the product weights.
* Configured Cart modifiers may be a list, rather than a single instance.
* Refactor shipping and payment modifiers in ``shop/modifiers/defaults.py`` into their own files
  ``shop/shipping/modifiers.py`` and ``shop/payment/modifiers.py``.
* Refactor shipping workflows in ``shop/shipping/base.py`` and ``shop/shipping/defaults.py`` into their
  own file ``shop/shipping/workflows.py``. Extract ``TRANSITION_TARGETS`` into their common base class.
* Refactor payment workflows in ``shop/payment/base.py`` and ``shop/shipping/defaults.py`` into their
  own file ``shop/payment/workflows.py``.
* Remove unused class ``ShippingProvider``.
* Add support for SendCloud_ integration.
* When partial delivery is configured, it now is possible to create multiple deliveries concurrently.
* Add configuration directive ``SHOP_MANUAL_SHIPPING_ID`` which shall be used to make the input field
  for the "Shipping ID" readonly.
* Add configuration directive ``SHOP_OVERRIDE_SHIPPING_METHOD`` which shall be used to allow the
  merchant to choose another shipping provider, instead of that selected by the customer.
* Model ``DeliveryItem`` was moved into ``shop.models.defaults.delivery_item`` to prevent accidental
  instantiation.
* Add ``OrderPaymentInline`` to ``OrderAdmin`` only, if status requires a payment or a refund.
* In ``OrderAdmin`` add tick to inform about a fullfilled Order payment.
* In ``ManualPaymentWorkflowMixin`` unified methods ``prepayment_partially_deposited()`` and
  ``prepayment_fully_deposited()`` into method ``payment_deposited()``.
* Add method ``__str__()`` to model ``BaseDelivery``.
* All models which can be used in the DialogForm, can offer a method ``as_text()`` which may render
  a nicely formatted representation of its content.
* Add method ``reorder_form_fields`` to Customer model, so that inheriting models can fix the order
  of form fields.

.. _SendCloud: https://www.sendcloud.eu/


0.12
====

* Adopted for django-angular version 2.0, which breaks its API. Invalid forms rejected by the server
  are send with a status code of 422 now. Check their changelog for details.
* Adopted to AngularJS-1.6.6, which required to replace all ``.success()`` handlers against
  a promise ``.then()``.
* RESTifyed the communication with the server, by using HTTP methods ``PUT`` and ``DELETE`` where
  appropriate.
* Rename ``PayInAdvanceWorkflowMixin`` to ``ManualPaymentWorkflowMixin``, since its purpose is to
  handle all incoming/outgoing payments manually.
* Move ``LeftExtensionPlugin`` and ``RightExtensionPlugin`` into module ``shop/cascade/extensions``
  and allow them to be used on the ``ShopOrderViewsPlugin`` as well.
* Refactored ``ShopReorderButtonPligin`` and ``ShopOrderAddendumFormPlugin`` to use the new
  ``djng-forms-set`` directive, as provided by **django-angular** version 2.0.
* ``ShopOrderAddendumFormPlugin`` can optionally render historical annotations for the given order.
* Added hook methods ``cancelable()`` and ``refund_payment()`` to ``BaseOrder`` to allow
  a better order cancelling interface.
* Paid but unshipped orders, now can be refunded. Possible be refactoring class
  ``CancelOrderWorkflowMixin``, which handles payment refunds.
* Add Order status to Order Detail View, so that the customer immediately sees what's going on.
* Reject method POST on Order List View.
* Fix: On re-add item to cart, use ``product_code`` to identify if that product already exists in cart.
* Do not render buttons and links related to the watch-list, when it is not available.
* Use Sekizai's templatetags ``{% add_data %}`` and ``{% with_data %}`` instead of Sekizai's
  postprocessors ``djng.sekizai_processors.module_config`` and ``djng.sekizai_processors.module_list``,
  which now are deprecated.
* Remove HTTP-Header ``X-HTTP-Method-Override`` and use PUT and DELETE requests natively.
* Remove django-angular dependency ``djng.url`` from project.
* Endpoints in JavaScript are always referenced through HTML. This eliminates the need for
  ``'djng.middleware.AngularUrlMiddleware'`` in ``MIDDLEWARE_CLASSES`` of your ``settings.py``.
* Use Django's internal password validator configuration ``AUTH_PASSWORD_VALIDATORS`` in your
  ``settings.py``.
* Refactored all templates for authentication forms to simplify inheritance and to use the promise
  chain (offered by django-angular 2.0). This allows to do fine-grained adoptions in the submit
  buttons behaviour.
* Decoupled all checkout forms. They don't require ``dialog.js``, ``forms-sets.js`` and ``auth.js``
  anymore. Instead use the functionality provided by django-angular 2.0 form directives.
* Use a REST endpoint to add, modify and delete multiple shipping and billing addresses. This
  simplifies the address forms. Remove ``shipping-address.js`` and replace it against a more generic
  ``address.js``.
* Use an event broadcast ``shop.carticon.caption`` to inform the carticon about changes in the cart.
* Add an overridable ``CartIconCaptionSerializer`` to specify what to render in the cart-icon.
* Use event broadcasting to inform the checkout forms if configured in summary mode. This decouples
  checkout form updates, from rendering their summary on another page or process step.
* Add operator to test Money type against booleans.
* Fix: Adopt polymorphic ModelAdmin-s to django-polymorphic>=1.0.
* Add to ``ShopProceedButton``: Disable button if any form in this set is invalid.
* Use vanilla Javascript in serverside JS-expressions.
* Decoupled ``CheckoutViewSet`` from ``CartViewSet``, so that the checkout only handles forms
  relevant to the checkout process.
* Endpoint ``digest`` in ``CheckoutViewSet``, returns a full description of all forms, plus the
  current cart's content. Fetching from there is emit a ``shop.checkout.digest`` event.
* Added directives ``shop-payment-method`` and ``shop-shipping-method`` which update the cart and
  emit a ``shop.checkout.digest`` event on change.
* Fix: All form input field get their own unique HTML ``id``. Previously some ``id``'s were used
  twice and caused collisions.
* Fix: Do not rebuild list of cart items, on each change of quantity.
* Separate ``CartController`` into itself and a ``CartItemControler``.
* Consistent naming of emit and broadcast events.
* Introduce ``CartSummarySerializer`` to retrieve a smaller checkout digest.
* In Shipping- and Payment Method Form, optionally show additional charges below the radio fields,
  depending on the selected method.
* Remove ``angular-message`` from the list of npm dependencies.
* Fix: Products with ``active=False`` are exempted from the catalog list views and accessing them
  raises a Not Found page.


0.11.7
======

* Fix: Python3 can not handle ``None`` type in max() function.
* Smoother animation when showing Payment form.


0.11.6
======

* Fix #708: Passing ``None`` when calling ``django.template.loader.select_template``
  in ``shop/cascade/catalog.py``.


0.11.5
======

* Fix: Money formatter did not work for search results.
* Image building uses docker-compose with official images instead of a crafted Dockerfile.


0.11.4
======

* Fix: Template context error while rendering Order List-View as Visitor.
* Fix: Money formatter to allow the usage of the thousand separator.
* Fix: It now is possible to use the ``ProductListView`` as the main CMS landing page.
* Fix: Template exception if left- or right extension was missing on the ``OrderList``
  and/or ``OrderDetail`` view.
* Add option to Catalog List View: It now is possible to redirect automatically onto a lonely
  product.
* Add options to override the add-to-cart template when using the appropriate
  CMS Cascade plugin.
* Add option to add a list of products to the navigation node serving a catalog list page.
* Upgrade external dependencies to their latest compatible versions.


0.11.3
======

* Fix: Problems with missing Left- and Right Extension Plugin.
* Ready for Django-1.11 if used with django-CMS-3.4.5
* Ready for django-restframework-3.7
* Tested with recent versions of other third party libraries.
* Fix issues with enum types when importing fixtures.
* Add Swedish Kronor to currencies.


0.11.2
=======

* Do not render buttons and links related to the watch-list, when it is not available.
* Fix: Adopt polymorphic ModelAdmin-s to django-polymorphic>=1.0.
* Use Sekizai's internal templatetags ``{% with_data ... %}`` and ``{% with_data %}`` to render Sekizai
  blocks ``ng-requires`` and ``ng-config`` rather than using the deprecated postprocessors
  ``djng.sekizai_processors.module_list`` and ``djng.sekizai_processors.module_config``. Adopt your
  templates accordingly as explained in :ref:`reference/client-framework`.
* Rename ``PayInAdvanceWorkflowMixin`` to ``ManualPaymentWorkflowMixin``, since its purpose is to
  handle all incoming/outgoing payments manually.
* Move ``LeftExtensionPlugin`` and ``RightExtensionPlugin`` into module ``shop/cascade/extensions``
  and allow them to be used on the ``ShopOrderViewsPlugin`` as well.
* ``ShopOrderAddendumFormPlugin`` can optionally render historical annotations for the given order.
* Added hook methods ``cancelable()`` and ``refund_payment()`` to ``BaseOrder`` to allow
  a better order cancelling interface.
* Paid but unshipped orders, now can be refunded. Possible be refactoring class
  ``CancelOrderWorkflowMixin``, which handles payment refunds.
* Add Order status to Order Detail View, so that the customer immediately sees what's going on.
* Add support for Python-3.6.


0.11.1
======

* Fix migration ``0007_notification`` to handle field ``mail_to`` correctly.
* Allow transition to cancel order only for special targets.
* Add operator to test Money type against booleans.


0.11
====

* Fix: :class:`shop.rest.renderers.CMSPageRenderer` always uses the template offered by the CMS page,
  rather than invoking method ``get_template_names()`` from the corresponding ``APIView`` class.
* Feature: Add class:`shop.rest.renderers.ShopTemplateHTMLRenderer` which is the counterpart of
  :class:`shop.rest.renderers.CMSPageRenderer`, usable for hardcoded Django views.
* Refactor: In examples *polymorphic* and *i18n_polymorphic*, renamed ``SmartPhone`` to ``SmartPhoneVariant``.
* Feature: In :class:`shop.money.fields.MoneyFormField` use a widget which renders the currency.
* Refactor: In :class:`shop.money.fields.MoneyField`, drop support for implicit default value, since it
  causes more trouble than benefit.
* Fix: Handle non-decimal types in :meth:`shop.money.fields.MoneyField.get_db_prep_save`.
* Fix: In AngularJS, changes on filters and the search field did not work on Safari.
* Fix: In :meth:`shop.views.auth.AuthFormsView.post` create a customer object from request for
  a visiting customers, rather than responding with *BAD REQUEST*.
* Fix: :meth:`shop.models.order.OrderManager.get_summary_url` only worked for views rendered
  as CMS page. Now it also works for static Django views.
* Simplified all methods ``get_urls()`` from all classes derived from ``CMSApp`` by exploiting
  CMS-PR 5898 introduced with django-CMS-3.4.4.
* Remove field ``customer`` from :class:`shop.serializers.order.OrderListSerializer`, since it
  interfered with the ``customer`` object on the global template_context namespace, causing template
  `shop/navbar/login-logout.html` to fail.
* Management command ``fix_filer_bug_965`` is obsolete with django-filer-1.2.8.
* Fix: Use caption in Order Detail View.
* Add Leaflet Map plugin from djangocms-cascade for demonstration purpose.
* Moved ``package.json`` into ``example/package.json`` (and with it ``node_modules``) since it
  shall be part of the project, rather than the Django app.
* Fix: In :meth:`shop.models.order.BaseOrderItem.populate_from_cart_item` the ``unit_price`` is
  takes from the ``cart_item``, rather than beeing recalculated.
* :class:`shop.cascade.cart.ShopCartPlugin` accepts two children: ``ShopLeftExtension`` and ``ShopRightExtension``
  which can be used to add plugins inside the cart's table footer.
* In :class:`shop.models.notification.Notification` renamed field ``mail_to`` to ``recipient`` and
  converted it to a ``ForeignKey``. Added an enum field ``notify`` to distinguish between different
  kinds of recipients.
* Refactored ``CustomerStateField`` into a reusable :class:`shop.models.fields.ChoiceEnumField` which
  can be used for both, ``Notify`` as well as ``CustomerState``.
* Adopted to **djangocms-cascade** version 0.14, which allows to render static pages using plugin
  descriptions in JSON.
* Added Paginator to Order List View.
* Refactored ``shop.app_settings`` into ``shop.conf.app_settings`` to be usable by Sphinx in docstrings.
* Added :meth:`shop.models.order.BaseOrder.get_all_transitions()` which returns all possible transitions
  for the the Order class.
* In :class:`shop.rest.renderers.ShopTemplateHTMLRenderer` do not pollute ``template_context`` with
  serialized data on the root level.
* Fix #623: Template ``auth/register-user.html`` did not validate properly, when Reset password was checked.
* Added AngularJS filter ``range`` to emulate enumerations in JavaScript.
* Fallback to hard-coded URL if CMS page for "Continue Shopping" is missing.


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
  otherwise required by the merchant implementation.
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
* Changed the default address models to be more generic.
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
