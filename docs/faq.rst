.. _faq:

============================
Frequently Asquest Questions
============================


Frontend Editing
================

Order Plugin
------------

**Editing the Order Plugin seems to be broken**

This has to do with the way, **django-CMS** handles the placeholder in its templates. Here the
problem is, that we're using the same template for both, the Order List View and their Detail
Views. The Detail Views however, are not managed by the CMS, but rather by a CMSApphook. The
latter confuses the CMS placeholder. It therefore is strongly recommended to edit the Order Page
only while in List View Mode.
