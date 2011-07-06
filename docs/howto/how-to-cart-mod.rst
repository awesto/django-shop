==============================
How to create a Cart modifier
==============================

Cart modifiers are simple plugins that allow you to define rules according to
which carts should be modified (and in what order).

Generally, this is how you implement a "bulk rebate" module, for instance.

.. warning::
   When using ``cart.extra_price_fields.append('your label', price)`` you might
   want to use ``from django.utils.translation import gettext as \_`` for your
   label in multilingual projects. Please make sure that you use ``gettext``
   indeed and not ``ugettext_lazy``!