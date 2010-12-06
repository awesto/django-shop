======================
Django-shop statement
======================

We realized that Django lacked a really reusable shop solution, with proper documentation, and a Djangonic "feel"
to it.

Goals:
======

* KISS: Keep It Simple, Stupid. The process of using a shop is simple - reading the code should be too.
* Djangonic. The shop should run on Django, not alongside it. We should not reinvent ways to solve problems Django already solves for us, such as settings management.
* Modular. Most shops have specificities. Instead of trying to solve all problems, let's have a clean core for which people can write modules.
* For developers. Django-Shop will not be an "out-of-the-box" shop solution. People will have to write templates for it. Shipping an example shop is not out of the question, but it *must* be well separated from a code perspective.
* Community firendly. This should be developed by and for the Django developers community. If we end up having no traction, that means there is no reason for this project to exist.

No-no's:
========

* Livesettings. Sorry.
* Shipping and maintaining templates in the basic codebase. This is wrong.




