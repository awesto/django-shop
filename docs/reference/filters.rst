.. _reference/filters:

=================================
Filter Products by its Attributes
=================================

Besides :ref:`reference/search`, adding some filter functionality to an e-commerce site is another
very important feature. Customers must be able to narrow down the list of available products to
a set of desired products using a combination of prepared filter attributes.

Since in **djangoSHOP** each product class declares its own database model with its own attributes,
often related by foreign keys to other data models, the filtering functionality must be implemented
by the merchant on top of the existing product models. Fortunately the REST framework in combination
with `django-filter`_ makes this a rather simple task.


Adding a filter to the List View
================================

In **djangoSHOP** listing the products normally is controlled by
:class:`shop.views.catalog.ProductListView` or :class:`shop.views.catalog.CMSPageProductListView`.
By default these View classes are configured to use the default filter backends as provided by the
REST framework. These filter backends can be configured globally through the settings variable
``DEFAULT_FILTER_BACKENDS``.

Additionally we can subclass the filter backends for each View class in our ``urls.py``. Say, we
need a special catalog filter, which groups our products by a certain product attribute. Then we
can create customized filter backend

.. code-block:: python
	:caption: filters.py

	from rest_framework.filters import BaseFilterBackend
	
	class CatalogFilterBackend(BaseFilterBackend):
	    def filter_queryset(self, request, queryset, view):
	        queryset = queryset.order_by('attribute__sortmetric')
	        return queryset

In ``urls.py``, where we route requests to the class :class:`shop.views.catalog.ProductListView`,
we then replace the default filter backends by our own implementation:

.. code-block:: python
	:caption: myshop/urls/catalog.py
	
	from django.conf.urls import url
	from rest_framework.settings import api_settings
	from shop.views.catalog import ProductListView
	from myshop.serializers import ProductSummarySerializer
	
	urlpatterns = [
	    url(r'^$', ProductListView.as_view(
	        serializer_class=ProductSummarySerializer,
	        filter_backends=[CatalogFilterBackend],
	    ),
	]

The above example is very simple but gives a rough impression on its possibilities.


Working with Django-Filter
--------------------------

django-filter_ is a generic, reusable application to alleviate writing some of the more mundane
bits of view code. Specifically, it allows users to filter down a queryset based on a model’s
fields, displaying the form to let them do this.

REST framework also includes support for `generic filtering backends`_ that allow you to easily
construct complex searches and filters.

By creating a class which inherit from :class:`django_filters.FilterSet`, we can build filters
against each attribute of our product. This filter then uses the passed in query parameters to
restrict the set of products available from our catalog:

.. code-block:: python
	:caption: myshop/filters.py

	import django_filters
	
	class ProductFilter(django_filters.FilterSet):
	    width = django_filters.RangeFilter(name='width')
	    props = django_filters.MethodFilter(action='filter_properties', widget=SelectMultiple)
	
	    class Meta:
	        model = OurProduct
	        fields = ['width', 'props']
	
	    def filter_properties(self, queryset, values):
	        for value in values:
	            queryset = queryset.filter(properties=value)
	        return queryset

This example assumes that ``OurProduct`` has a numeric attribute named ``width`` and a many-to-many
field named ``properties``.

We then can add this filter to the list view for our products. In **djangoSHOP** we normally do
this through the url patterns:

.. code-block:: python
	:caption: myshop/urls.py

	urlpatterns = [
	    url(r'^$', ProductListView.as_view(
	        serializer_class=ProductSummarySerializer,
	        filter_class=ProductFilter,
	    )),
	    # other patterns
	]

By appending ``?props=17`` to the URL, the above filter class will restrict the products in our list 
view to those with a ``property`` of 17.


Populate the Render Context
---------------------------

Filtering functionality without an appropriate user interface doesn't make much sense. Therefore,
when rendering the product's list view, we might want to add some input fields or special links, so
that the customer can narrow down the result set. To do this, the rendering template requires
additional context data.

Since **djangoSHOP** honours the principle of cohesion, each filter set is responsible for providing
the context required to render its specific filtering parameters. This optional extra context must
be a dictionary named ``render_context``, respectively a method ``get_render_context(request)``
which must return such a dictionary.

When rendering HTML pages, this extra context then is available and can be used to render various
tag filtering elements.

.. _django-filter: http://django-filter.readthedocs.org/en/latest/usage.html
.. _generic filtering backends: http://www.django-rest-framework.org/api-guide/filtering/#generic-filtering
