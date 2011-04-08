
=======
 Taxes
=======

Why
===

On a first tought, shops need some knowledge about taxes to be able to
display prices correctly. It may be required to display net or gross
prices, this may depend on the customer.

It may also be required to do some tax calculations, this will at
least be the case during the checkout process. Taxes may also have to
be applied to shipment costs in some way and depend on the customer
and the delivery location.

If one also wants to generate invoices from a shop, there might be
also further requirements.


What to do in the core implementation
=====================================

Maybe it is possible to find a simple solution to start with and try
to be extendable:

* Find a simple solution which is sufficient for simple shops. (?)

* Try to do models in a way that most tax requirements can be solved
  by extended implementations.

* Check which information is required to determine the tax rules to
  apply. This information should be made available to tax
  implementations.



What do others?
===============

Try to not reinvent the wheel: Other shop systems / frameworks will
contain solutions to this problem. But also ERP-Systems will contain
solutions to this problem.

Maybe it is wise to have a look at projects like Tryton
(http://tryton.org).
