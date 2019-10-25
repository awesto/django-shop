.. _reference/filters:

=================================
Filter Products by its Attributes
=================================

Besides :ref:`reference/search`, adding a filtering functionality to an e-commerce site is another
very important feature. Customers must be able to narrow down a huge list of available products to
a small set of desired products using a combination of prepared filter attributes.

In **django-SHOP**, we model each product according to its own properties, the color for instance.
The customer then might filter the listed products, selecting one or more of the given properties,
the color "blue" for instance.

Therefore, when creating a database schema, we add that property to our product model. This can
either be a hard coded list of enumerated choices, or if we need a more flexible approach, a foreign
key onto another model referring to that specific property. If our product model allows more than
one attribute of the same property, then we would use a many-to-many-key in our database.

The contents of this additional property model (or hard coded property list), then is used to
create a set of available filtering options, from which the customer can select one (if allowed,
also more) options to narrow down the list of products with that specific attributes.

Fortunately, the REST framework in combination with `Django Filter`_, makes it a rather simple task
to implement this kind of filtering functionality on top of the existing product models.


Adding a Filter to the List View
================================

In **django-SHOP** showing a list of products, normally is controlled by the classes
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

	urlpatterns = [
	    url(r'^$', ProductListView.as_view(
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
restrict the set of products available from our current catalog view. Presume that our product model
uses a foreign key onto a model holding all manufactures. We then can create a simple filter class
to restrict our list view onto a certain manufacturer:

.. code-block:: python
	:caption: myshop/filters.py

	from django.forms import forms, widgets
	import django_filters
	from djng.forms import NgModelFormMixin
	from myshop.models.product import MyProduct, Manufacturer

	class FilterForm(NgModelFormMixin, forms.Form):
	    scope_prefix = 'filters'

	class ProductFilter(django_filters.FilterSet):
	    manufacturer = django_filters.ModelChoiceFilter(
	        queryset=Manufacturer.objects.all(),
	        widget=Select(attrs={'ng-change': 'filterChanged()'}),
	        empty_label="Any Manufacturer")

	    class Meta:
	        model = MyProduct
	        form = FilterForm
	        fields = ['manufacturer']

	    @classmethod
	    def get_render_context(cls, request, queryset):
	        """
	        Prepare the context for rendering the filter.
	        """
	        filter_set = cls()
	        # we only want to show manufacturers for products available in the current list view
	        filter_field = filter_set.filters['manufacturer'].field
	        filter_field.queryset =filter_field.queryset.filter(
	            id__in=queryset.values_list('manufacturer_id'))
	        return dict(filter_set=filter_set)

To this filter class we can combine as many fields as we need, but in this example, we just use
the foreign key to the manufacturer model. For all available filter field types, please check the
appropriate documentation in `Django Filter`_.

We then can add this filter class to our product list view. In **django-SHOP** this normally is done
through the url patterns:

.. code-block:: python
	:caption: myshop/urls.py

	urlpatterns = [
	    url(r'^$', ProductListView.as_view(
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

Since **django-SHOP** honours the principle of cohesion, each filter set is responsible for providing
the context required to render its specific filtering parameters. This extra context must be
provided by a class-method named ``get_render_context(request, queryset)``, which must return
a dictionary containing an instance of that filter set.

While rendering HTML pages, this extra context then can be used to render various tag filtering
elements, such as a ``<select>``-box. Since our ``ProductFilter`` can be rendered as form fields,
we just have to use this Django template:

.. code-block:: django

	{{ filter.filter_set.form }}


The Client Side
---------------

If your site uses the provided AngularJS directive ``<shop-list-products>``, we typically want to
use that as well, when the customer applies a product filter. Therefore this directive listens on
events named ``shop.catalog.filter`` and queries the backend with the given properties. This allows
us to add a set of filter options to the product's list view, without having to care about how to
fetch that filtered list from the server.

Since we don't event want to care about controlling change events on the filtering ``<select>`` box,
**django-SHOP** is shipped with a reusable directive named ``shop.product.filter``.

Sample HTML snippet:

.. code-block:: django

	<div shop-product-filter="manufacturer">
	  {{ filter.filter_set.form }}
	</div>

or if your filter set forms uses more than one attribute:

.. code-block:: django

	<div shop-product-filter="['manufacturer', 'brand']">
	  {{ filter.filter_set.form }}
	</div>

The Angular directive ``shop.product.filter`` is declared inside the shop's ``shop/js/filters.js``
module, so make sure to include that file. Additionally, that module must be initialized while
bootstrapping our Angular application:

.. code-block:: javascript

	angular.module('myShop', [..., 'django.shop.filter', ...]);

Each time the customer selects another manufacturer, the function ``filterChanged`` emits
an event intercepted by the AngularJS directive ``shopListProducts``, which consequently
fetches a list of products using the filtering class as shown above.

Apart from forwarding changes detected in our ``<select>`` box, this directive also modifies the
URL and appends the selected properties. This is required, whenever the user navigates away from
the product's list view and returns back, so that the same filters are applied. Additionally the
directive clears the search query field, because full text search in combination with property
filtering is confusing and doesn't make sense.

.. _Django Filter: http://django-filter.readthedocs.org/en/latest/usage.html
.. _generic filtering backends: http://www.django-rest-framework.org/api-guide/filtering/#generic-filtering
