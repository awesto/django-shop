============
Architecture
============

This document should gather all the pre-code architecture requirements/research.

Core system
===========

Generally, the shop system can be seen as tree different phases, with two different problems to
solve:


The shopping phase
------------------

From a customers perspective, this is where we look around at different products, presumably in
different categories. We denote this as the catalog list and catalog detail views. Here we add
the desired products to our shopping cart, which sums up and keeps track on the total.


The checkout process
--------------------

As the name implies, this is a "workflow" type of problem: we must be able to remove or change
the number of items in the cart. 
