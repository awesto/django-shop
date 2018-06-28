.. _reference/cart-icon:

=========================
Controlling the Cart Icon
=========================

On e-commerce sites, typically a cart- or basket symbol is located on the top right corner of the
navigation bar and clicking on it, normally loads the cart page.

Together with the cart icon, we often want to display an additional caption, such as the number
of items and/or the cart's total. The cart item typically is rendered using the templatetag
``{% cart_icon %}``. It can be styled using the template ``myshop/templatetags/cart-icon.html``,
or if it doesn't exist, falls back on ``shop/templatetags/cart-icon.html``.


Cart Icon Caption
=================

This is where the client-side cart controller enters the scene. Adding product to –, or editing
the cart changes the number of items and/or the cart's total. Therefore we must update its caption
whenever we detect a modification in the cart. A typical use pattern, for example is::

    <a href="{% page_url 'shop-cart' %}">
        <i class="fa fa-shopping-cart fa-fw fa-lg"></i>
        <shop-carticon-caption caption-data="{num_items: {{ cart.num_items|default:0 }} }"></shop-carticon-caption>
    </a>

The AngularJS directive ``<shop-carticon-caption ...>`` is itself styled using an Angular template
such as::

    <script id="shop/carticon-caption.html" type="text/ng-template">
        <ng-pluralize count="caption.num_items" when="{'1': '{% trans "1 Item" context "cart icon" %}', 'other': '{% trans "{} Items" context "cart icon" %}'}"></ng-pluralize>
    </script>

Whenever this AngularJS directive receives an event of type ``shop.carticon.caption``, then it
updates the cart icon's caption with the current state of the cart. The emitter of such an event
typically is the cart editor or an add-to-cart directive. If this function has already computed
the new caption data, it may send it to the cart item, such as:

.. code-block:: javascript

    $scope.$emit('shop.carticon.caption', caption_data);

otherwise, if it emits the signal without object, the AngularJS directive ``shopCarticonCaption``
will fetch the updated caption data from the server. The latter invokes an additional HTTP request
but is useful, if the caption shall for instance contain the cart's total, since this has to be
computed on the server anyway.
