.. _howto/handling-taxes:

======
Taxes
======

As a general rule, the unit price of a product, shall always contain the net price. When our
products show up in the catalog, their method ``get_price(request)`` is consulted by the framework.
Its here where you add tax, depending on the tax model to apply. See below.


Use Cart Modifiers to handle tax
================================



American tax model
------------------


European tax model
------------------


Other considerations
====================

Try to not reinvent the wheel: Other shop systems / frameworks will
contain solutions to this problem. But also ERP-Systems will contain
solutions to this problem.

Maybe it is wise to have a look at projects like Tryton
(http://tryton.org).
