.. _reference/filters:

=================================
Filter Products by its Attributes
=================================

Besides :ref:`reference/search`, adding a filtering functionality to an e-commerce site is another
very important feature. Customers must be able to narrow down a huge list of available products to
a small set of desired products using a combination of prepared filter attributes.

In **djangoSHOP**, we model each product according to it's own properties, the color for instance.
The customer then might filter the listed products, selecting one or more of the given properties,
the color "blue" for instance.

Therefore, when creating a database schema, we add that property to our product model. This can
either be a hard coded list of enumerated choices, or if we need a more flexible approach, a foreign
key onto another model referring to that specific property. If our product model allows more that
one instance of the same property, then we would use a many-to-many-key in our database

The contents of this additional property model (or hard coded property list), then is used to
create a set of available filtering options, from which the customer can select one (if allowed,
also more) options to narrow down the list of products with that specific properties.

Fortunately, the REST framework in combination with `Django Filter`_, makes it a rather simple task
to implement this kind of filtering functionality on top of the existing product models.


Adding a Filter to the List View
================================

In **djangoSHOP** listing the products normally is controlled by the classes
:class:`shop.views.catalog.ProductListView` or :class:`shop.views.catalog.CMSPageProductListView`.
By default these View classes are configured to use the default filter backends as provided by the
REST framework. These filter backends can be configured globally through the settings variable
``DEFAULT_FILTER_BACKENDS``.

Additionally we can subclass the filter backends for each View class in our ``urls.py``. Say, we
need a special catalog filter, which groups our products by a certain product attribute. Then we
can create a customized filter backend

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

`Django Filter`_ is a generic, reusable application to alleviate writing some of the more mundane
bits of view code. Specifically, it allows users to filter down a queryset based on a model’s
fields, displaying the form to let them do this.

REST framework also includes support for `generic filtering backends`_ that allow you to easily
construct complex searches and filters.

By creating a class which inherits from :class:`django_filters.FilterSet`, we can build filters
against each attribute of our product. This filter then uses the passed in query parameters to
restrict the set of products available from our catalog. Presume that our product model uses
a foreign key onto a model holding all manufactures. We then can create a simple filter class
to restrict our list view onto a certain manufacturer:

.. code-block:: python
	:caption: myshop/filters.py

	import django_filters
	from myshop.models.manufacturer import Manufacturer

	class ProductFilter(django_filters.FilterSet):
	    manufacturer = django_filters.ModelChoiceFilter(queryset=Manufacturer.objects.all())

	    class Meta:
	        model = MyProduct
	        fields = ['manufacturer']

	    @classmethod
	    def get_render_context(cls, request, queryset):
	        """
	        Prepare the context for rendering the filter.
	        We only want to show manufacturers for the list available in the current list view.
	        """
	        manufacturer_ids = set([i[0] for i in queryset.values_list('manufacturer')])
	        return {'manufacturers': Manufacturer.objects.filter(id__in=manufacturer_ids)}

To this filter class we can combine as many fields as we need, but in this example, we just use
the foreign key to the manufacturer model. For all available filter field types, please check the
appropriate documentation in `Django Filter`.

We then can add this filter class to the list view of our products. In **djangoSHOP** we normally
do this through the url patterns:

.. code-block:: python
	:caption: myshop/urls.py

	urlpatterns = [
	    url(r'^$', ProductListView.as_view(
	        serializer_class=ProductSummarySerializer,
	        filter_class=ProductFilter,
	    )),
	    # other patterns
	]

By appending ``?manufacturer=7`` to the URL, the above filter class will restrict the products
in our list view to those manufactured by the database entry with a primary key of 7.


Populate the Render Context
---------------------------

Filtering functionality without an appropriate user interface doesn't make much sense. Therefore,
when rendering the product's list view, we might want to add some input fields or special links, so
that the customer can narrow down the result set. To do this, the rendering template requires
additional context data.

Since **djangoSHOP** honours the principle of cohesion, each filter set is responsible for providing
the context required to render its specific filtering parameters. This optional extra context must
be provided by a class-method named ``get_render_context(request, queryset)``, which must return
such a dictionary.

When rendering HTML pages, this extra context then is available and can be used to render various
tag filtering elements, such as a ``<select>``-box.


The Client Side
---------------

If your site uses the provided AngularJS directive ``<shop-list-products>``, we typically want to
use it as well, when the customer applies a product filter. Therefore this directive listens on
events named ``shopCatalogFilter`` and queries the backend with the given properties. This allows
us add a set of filter options to the product's list view, without having to care about how to fetch
that filtered list from the server.

If we render the filtering selection in our list view such as:

.. code-block:: html

	<div ng-controller="filterManufacturer" style="margin-bottom: 10px;">
	  <label for="manufacturer">Chose Manufacturer:</label>
	  <select name="manufacturer" ng-change="filterChanged()" ng-model="manufacturer">
	    <option>any</option>
	    {% for manufacturer in filter.manufacturers %}
	    <option value="{{ manufacturer.id }}">{{ manufacturer.name }}</option>
	    {% endfor %}
	  </select>
	</div>

we then can connect it to a very simple AngularJS controller:

.. code-block:: javascript

	app.controller('filterManufacturer', ['$scope', function($scope) {
	  $scope.filterChanged = function() {
	    $scope.$emit('shopCatalogFilter', {manufacturer: $scope.manufacturer});
	  };
	}]);

Each time the customer selects another manufacturer, the function ``filterChanged`` emits
an event intercepted by the AngularJS directive ``shopListProducts``, which consequently
fetches a list of products using the filtering class as shown above.

.. _Django Filter: http://django-filter.readthedocs.org/en/latest/usage.html
.. _generic filtering backends: http://www.django-rest-framework.org/api-guide/filtering/#generic-filtering
