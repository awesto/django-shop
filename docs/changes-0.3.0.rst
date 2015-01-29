
Changes for 0.3.0
=================

Please note that starting with version 0.3, the **django-shop** API will break a lot of stuff.
Therefore don't try to upgrade. Install this version of **django-shop** and migrate your models.

* Using a completly different approach on handling abstract models, see issue ..
  * Every time, django shop internally referrs to another abstract base class, the corresponding
    materialized model is used. This
* Renamed for convention with other shop systems:
  * Shipping -> Delivery
  * Billing -> Invoice
  * date_created -> created_at
  * last_updated -> updated_at
* Changed the two OneToOne relations from model Address to User, one was used for shipping, one for
  billing. Now abstract BaseAddress refers to the User by a single ForeignKey giving the ability to
  link more than one address to each user. Additionally each address has a priority field for
  delivery and invoices, so that the latest used address is offered to the client.
* Replaced model shop.models.User by the configuration directive settings.AUTH_USER_MODEL, to be
  conformant with Django documentation.
* The cart now is always stored inside the database; there is no more distinction between session
  based carts and database carts. Carts for anonymous users are retrieved using the visitor's
  session_key. Therefore we don't need any utility function ``get_or_create_cart`` anymore.
  Everything is handled by the new CartManager.
