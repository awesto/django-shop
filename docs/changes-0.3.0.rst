
Changes for 0.3.0
=================

Please note that starting with version 0.3, the **django-shop** API will break a lot of stuff.
Therefore don't try to upgrade. Install this version of **django-shop** and migrate your models.

* Using a completely different approach on handling abstract models, see issue ..

  * Every time, django shop internally refers to another abstract base class, the corresponding
    materialized model is used. This

* Renamed for convention with other Django application:

  * date_created -> created_at
  * last_updated -> updated_at
  * ExtraOrderPriceField -> BaseOrderExtraRow
  * ExtraOrderItemPriceField -> BaseItemExtraRow
  * OrderExtraInfo -> Order.annotations

* Changed the two OneToOne relations from model Address to User, one was used for shipping, one for
  billing. Now abstract BaseAddress refers to the User by a single ForeignKey giving the ability to
  link more than one address to each user. Additionally each address has a priority field for
  shipping and invoices, so that the latest used address is offered to the client.

* Replaced model shop.models.User by the configuration directive settings.AUTH_USER_MODEL, to be
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

* The templatetags ``shop_tags`` have been removed, since they don't make sense anymore.

* Cart and CartItem are available through a REST interface. This allows us to build MVC on top of
  that.

* Delegated responsibility to Cart modifiers.

* Backend pools for Payment and Shipping have been removed. Instead, a Cart Modifier can inherit
  from ``PaymentModifier`` or ``ShippingModifier``. This allows to reuse the Cart Modifier Pool for
  these backends and use the modifiers logic for added extra rows to he carts total.

* The table OrderExtraRow and OrderItemExtraRow has been replaced by a JSONField extra_rows in
  model OrderModel and OrderItemModel.

Some ideas
----------
Volatile data in the cart and the cart items, such as sub- and line-totals, as computed by the Cart
Modifiers, and cached with the model objects. This knowledge is lost with each new request.
Therefore it would be better to keep it inside the Django cache.

On startup, Django should iterate over all session keys and remove anonymous carts, where the
session is gone. Maybe there is a signal handler which informs us about expired sessions.

If a cart is filled and the user logs in, merge the former anonymous cart with the now authenticated
cart.

CartModifiers should be able to calculate amounts, which are only displayed, but not added to the
total price. This for instance can be useful to show the VAT portion of a product, already listed
with its gross price.
