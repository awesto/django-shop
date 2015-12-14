===========
Order Views
===========

In **djangoSHOP**, the order list- and order-detail views follows the same idea as all other pages
– they are managed by the CMS. Change into the Django admin backend and enter into the CMS page
tree. A good position in that tree for adding the Order list-view page is below the "Info" section,
but any other page will work as well. Do so by clicking onto the button named **Add page**.

As the page title chose something such as "Your Orders", then enter into the "Advanced settings" as
found on the bottom of the page.

As the template, use the "Default template", or any other template with a placeholder able to accept
a large table.

Fill the input field named **Id** with the identifier "shop-order". This is required by some
templates which link directly onto the order list-view page. If unset, these links will not work.

The Order Views must be rendered by their own CMS apphook_. Locate the field **Application** and
chose "Orders".

Click onto **View on site** to change into front-end editing mode. Locate the main placeholder and
add a **Row** followed by a **Column** plugin from the section **Bootstrap**. Below that column add
a **Order View** plugin from section **Shop**. Then publish the page, it now should display an
list containing your order:

|order-list-view| 

.. |order-list-view| image:: /_static/order/list-view.png

Clicking onto one of those orders opens the detail view:

|order-detail-view| 

.. |order-detail-view| image:: /_static/order/detail-view.png

This is a historical snapshot of the cart in the moment of purchase. If in the meantime the price
of the product, the tax rate, the shipping costs or whatever changed, then that order object always
will remember the correct historical data. This even applies to translations. Strings are translated
into their natural language on the moment of purchase. Therefore the labels of added by the cart
modifiers always are rendered in the language used during the checkout process.

Although its possible to view the order in a different language, keep in mind that some translated
strings then might be in a different language than the rest of the page.


Change the templates
====================

The path of the templates used to render the order views is constructed using the following rules:

* Look for a folder named according to the project's name, ie. ``settings.SHOP_APP_LABEL`` in lower
  case. If no such folder can be found, then use the folder named ``shop``.
* Search for a subfolder named ``order``.
* Search for a template named ``list.html`` or ``detail.html``.

These templates are written to be easily extensible by the customized templates. To override them,
add a template with the path, say ``myshop/order/list.html`` to the projects template folder.

.. _apphook: http://docs.django-cms.org/en/latest/how_to/apphooks.html
