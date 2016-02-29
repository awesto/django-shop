.. _reference/filters:

=================================
Filter Products by its Attributes
=================================

Besides :ref:`reference/search`, adding some filter functionality to an e-commerce site is another
very important feature. Customers must be able to narrow down the list of available products to
a set of desired products using a combination of prepared filter attributes.

Since in **djangoSHOP** each product class declares its own database model with its own attributes,
often related with foreign data models, filtering must be implemented by the merchant on top of the
existing product models. Fortunately the REST framework in combination with `Django Filter`_ makes
this a rather simple task.


Adding a filter to the List View
================================

In **djangoSHOP** listing the products normally is controlled by
:class:`shop.views.catalog.ProductListView` or :class:`shop.views.catalog.CMSPageProductListView`.
By default these View classes are configured to use the default filter backends as provided by the
REST framework. These filter backends can be configured globally through the settings variable
``DEFAULT_FILTER_BACKENDS``.

Additionally we can override the filter backends for each View class in our ``urls.py``. Say, we
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
	
	from django.conf.urls import patterns, url
	from rest_framework.settings import api_settings
	from shop.views.catalog import ProductListView
	from myshop.serializers import ProductSummarySerializer
	
	urlpatterns = patterns('',
	    url(r'^$', ProductListView.as_view(
	        serializer_class=ProductSummarySerializer,
	        filter_backends=[CatalogFilterBackend],
	    ),
	)

The above example is very simple but gives a rough impression on its possibilities. By creating
a class which inherit from :class:`django_filters.FilterSet`, we can build filters against each
attribute of our product. This filter the uses the passed in query parameters to restrict the
set of products available from our catalog:

.. code-block:: python
	:caption: myshop/filters.py

	import django_filters
	
	class PanelFilter(django_filters.FilterSet):
	    width = django_filters.RangeFilter(name='panel_width')
	    props = django_filters.MethodFilter(action='filter_properties', widget=SelectMultiple)
	
	    class Meta:
	        model = TextilePanel
	        fields = ['width', 'props']
	
	    def filter_properties(self, queryset, values):
	        for value in values:
	            queryset = queryset.filter(properties=value)
	        return queryset


.. _django-filter: http://django-filter.readthedocs.org/en/latest/usage.html
