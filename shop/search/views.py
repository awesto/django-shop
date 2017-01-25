# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from rest_framework.mixins import ListModelMixin
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.settings import api_settings
from drf_haystack.generics import HaystackGenericAPIView

from shop.models.product import ProductModel
from shop.rest.filters import CMSPagesFilterBackend
from shop.rest.renderers import CMSPageRenderer
from shop.rest.money import JSONRenderer
from shop.views.catalog import ProductListView


class SearchView(ListModelMixin, HaystackGenericAPIView):
    """
    A generic view to be used for rendering the result list while searching.
    """
    renderer_classes = (CMSPageRenderer, JSONRenderer, BrowsableAPIRenderer)
    serializer_class = None  # to be set by SearchView.as_view(serializer_class=...)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_template_names(self):
        return [self.request.current_page.get_template()]


class AddFilterContextMixin(object):
    def get_renderer_context(self):
        renderer_context = super(AddFilterContextMixin, self).get_renderer_context()
        if self.view.filter_class and renderer_context['request'].accepted_renderer.format == 'html':
            # restrict to products associated to this CMS page only
            queryset = self.view.product_model.objects.filter(self.view.limit_choices_to)
            queryset = CMSPagesFilterBackend().filter_queryset(self.request, queryset, self)
            renderer_context['filter'] = self.view.filter_class.get_render_context(self.request, queryset)
        return renderer_context


class CMSPageCatalogWrapper(object):
    """
    Wraps the view classes :class:`shop.views.catalog.ProductListView` and
    :class:`shop.search.views.SearchView` into a callable which behaves like a
    Django View class, but dispatches requests between both of them depending on
    the query params.

    Usage: Add it to the urlpatterns responsible for rendering the catalog's list view:
    ```
    urlpatterns = [
        url(r'^$', CMSPageCatalogWrapper.as_view(
            filter_class=CustomFilterSet,
        )),
    ```

    In addition to ``filter_class`` you may override other attributes:

    :param renderer_classes: A list or tuple of REST renderer classes.

    :param product_model: The product model onto which the filter set is applied.

    :param limit_choices_to: Limit the queryset of product models to these choices.

    :param filter_class: A filter set which must be inherit from :class:`django_filters.FilterSet`.

    :param search_serializer_class: The serializer class used to process the queryset returned
        by Haystack, while performing an autocomplete lookup.

    :param model_serializer_class: The serializer class used to process the queryset returned
        by the catalog's product list view, while using a filter set.

    :param filter_backends: The filter backends used to narrow down the catalog's product list view.

    :param cms_pages_fields: Specify the fields used by the Product model to assign them to
        categories.
    """
    renderer_classes = (CMSPageRenderer, JSONRenderer, BrowsableAPIRenderer)
    product_model = ProductModel
    limit_choices_to = models.Q()
    search_serializer_class = None  # must be overridden by CMSPageCatalogWrapper.as_view()
    model_serializer_class = None  # must be overridden by CMSPageCatalogWrapper.as_view()
    filter_class = None  # may be overridden by CMSPageCatalogWrapper.as_view()
    filter_backends = [CMSPagesFilterBackend] + list(api_settings.DEFAULT_FILTER_BACKENDS)
    cms_pages_fields = ['cms_pages']

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def as_view(cls, **initkwargs):
        for key in initkwargs:
            if not hasattr(cls, key):
                msg = "{0}() received an invalid keyword {1}. Method as_view() only " \
                      " accepts arguments that are already attributes of the class."
                raise TypeError(msg.format(cls.__name__, key))

        self = cls(**initkwargs)

        attrs = dict(view=self, renderer_classes=self.renderer_classes)
        self.search_view = type(str('CatalogSearchView'), (AddFilterContextMixin, SearchView), attrs).as_view(
            serializer_class=self.search_serializer_class,
        )

        attrs.update(filter_backends=self.filter_backends, filter_class=self.filter_class,
                     cms_pages_fields=self.cms_pages_fields)
        self.list_view = type(str('CatalogListView'), (AddFilterContextMixin, ProductListView), attrs).as_view(
            serializer_class=self.model_serializer_class,
        )

        return self

    def __call__(self, request):
        if request.GET.get('q'):
            return self.search_view(request)
        return self.list_view(request)
