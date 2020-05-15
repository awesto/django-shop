import os
from urllib.parse import urlsplit

from django.db import models
from django.http.response import Http404, HttpResponseRedirect
from django.http.request import QueryDict
from django.shortcuts import get_object_or_404
from django.utils.cache import add_never_cache_headers
from django.utils.encoding import force_str
from django.utils.translation import get_language_from_request

from rest_framework import generics
from rest_framework import pagination
from rest_framework import status
from rest_framework import views
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param

from cms.views import details

from shop.conf import app_settings
from shop.models.product import ProductModel
from shop.rest.filters import CMSPagesFilterBackend
from shop.rest.money import JSONRenderer
from shop.rest.renderers import ShopTemplateHTMLRenderer, CMSPageRenderer
from shop.serializers.bases import ProductSerializer
from shop.serializers.defaults.catalog import AddToCartSerializer


class ProductListPagination(pagination.LimitOffsetPagination):
    """
    If the catalog's list is rendered with manual pagination, typically we want to render all rows
    without "widow" items (widows are single items spawning a new row). By using a limit of 16
    items per page, we can render 2 and 4 columns without problem, however whenever we need 3 or 5
    columns, there is one widow item, which breaks the layout. To prevent this problem, configure
    the ``ProductListView`` to use this pagination class. It behaves so that the last product items
    of a page, reappear on the next page. The number of reappearing items is set to 3. It can be
    modified by changing ``overlapping`` to a different value.

    By virtue, the rendering view can not know the current media breakpoint, and hence the number
    of columns. Therefore simply hide (with ``display: none;``) potential widow items by using the
    media breakpoints provided by CSS (see ``static/shop/css/prevent-widows.scss`` for details).
    Since the last product items overlap with the first ones on the next page, no items are hidden.
    This allows us to switch between layouts with different number of columns, keeping the last row
    of each page in balance.
    """
    template = 'shop/templatetags/paginator.html'
    default_limit = 16
    overlapping = 1

    def adjust_offset(self, url, page_offset):
        if url is None:
            return
        (scheme, netloc, path, query, fragment) = urlsplit(force_str(url))
        query_dict = QueryDict(query)
        try:
            offset = pagination._positive_int(
                query_dict[self.offset_query_param],
            )
        except (KeyError, ValueError):
            pass
        else:
            if offset > page_offset:
                url = replace_query_param(url, self.offset_query_param, max(0, offset - self.overlapping))
            elif offset < page_offset:
                url = replace_query_param(url, self.offset_query_param, offset + self.overlapping)
        return url

    def get_html_context(self):
        context = super().get_html_context()
        page_offset = self.get_offset(self.request)
        context['previous_url'] = self.adjust_offset(context['previous_url'], page_offset)
        context['next_url'] = self.adjust_offset(context['next_url'], page_offset)
        for k, pl in enumerate(context['page_links']):
            url = self.adjust_offset(pl.url, page_offset)
            page_link = pagination.PageLink(url=url, number=pl.number, is_active=pl.is_active, is_break=pl.is_break)
            context['page_links'][k] = page_link
        return context


class ProductListView(generics.ListAPIView):
    """
    This view is used to list all products which shall be visible below a certain URL.

    Usage: Add it to the urlpatterns responsible for rendering the catalog's views. The
    file containing this patterns can be referenced by the CMS apphook used by the CMS pages
    responsible for rendering the catalog's list view.
    ```
    urlpatterns = [
        ...
        url(r'^(?P<slug>[\w-]+)/?$', ProductRetrieveView.as_view(**params)),  # see below
        url(r'^$', ProductListView.as_view()),
    ]
    ```

    These attributes can be added to the ``as_view(**params)`` method:

    :param renderer_classes: A list or tuple of REST renderer classes.

    :param product_model: The product model onto which the filter set is applied.

    :param serializer_class: The serializer class used to process the queryset returned
        by the catalog's product list view.

    :param limit_choices_to: Limit the queryset of product models to these choices.

    :param filter_class: A filter set which must be inherit from :class:`django_filters.FilterSet`.

    :param pagination_class: A pagination class inheriting from :class:`rest_framework.pagination.BasePagination`.

    :param redirect_to_lonely_product: If ``True``, redirect onto a lonely product in the
        catalog. Defaults to ``False``.
    """
    renderer_classes = (CMSPageRenderer, JSONRenderer, BrowsableAPIRenderer)
    product_model = ProductModel
    serializer_class = app_settings.PRODUCT_SUMMARY_SERIALIZER
    limit_choices_to = models.Q()
    filter_class = None
    pagination_class = ProductListPagination
    redirect_to_lonely_product = False

    def get(self, request, *args, **kwargs):
        if self.redirect_to_lonely_product and self.get_queryset().count() == 1:
            redirect_to = self.get_queryset().first().get_absolute_url()
            return HttpResponseRedirect(redirect_to)

        response = self.list(request, *args, **kwargs)
        # TODO: we must find a better way to invalidate the cache.
        # Simply adding a no-cache header eventually decreases the performance dramatically.
        add_never_cache_headers(response)
        return response

    def get_queryset(self):
        qs = self.product_model.objects.filter(self.limit_choices_to, active=True)
        # restrict queryset by language
        if hasattr(self.product_model, 'translations'):
            language = get_language_from_request(self.request)
            qs = qs.prefetch_related('translations').filter(translations__language_code=language)
        qs = qs.select_related('polymorphic_ctype')
        return qs


class SyncCatalogView(views.APIView):
    """
    This view is used to synchronize the number of items in the cart from using the catalog's list
    view. It is intended for sites, where we don't want having to access the product's detail
    view for adding each product individually to the cart.

    Use Angular directive <ANY shop-sync-catalog-item="..."> on each catalog item to set up
    the communication with this view.

    To the ``urlpatterns`` responsible for the list view, add
    ```
    urlpatterns = [
        ...
        url(r'^sync-catalog$', SyncCatalogView.as_view(
            serializer_class=SyncCatalogSerializer,
        )),
        ...
    ]
    ```
    to the URLs as specified by the merchant's implementation of its catalog list.

    The class ``SyncCatalogSerializer`` must be provided by the merchant implementation.
    """
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)
    product_model = ProductModel
    product_field = 'product'
    serializer_class = None  # must be overridden by SyncCatalogView.as_view()
    filter_class = None  # may be overridden by SyncCatalogView.as_view()
    limit_choices_to = models.Q()

    def get_context(self, request, **kwargs):
        filter_kwargs = {'id': request.data.get('id')}
        if hasattr(self.product_model, 'translations'):
            filter_kwargs.update(translations__language_code=get_language_from_request(self.request))
        queryset = self.product_model.objects.filter(self.limit_choices_to, **filter_kwargs)
        product = get_object_or_404(queryset)
        return {self.product_field: product, 'request': request}

    def get(self, request, *args, **kwargs):
        context = self.get_context(request, **kwargs)
        serializer = self.serializer_class(context=context, **kwargs)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        context = self.get_context(request, **kwargs)
        serializer = self.serializer_class(data=request.data, context=context)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddToCartView(views.APIView):
    """
    Handle the "Add to Cart" dialog on the products detail page.
    """
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)
    product_model = ProductModel
    serializer_class = AddToCartSerializer
    lookup_field = lookup_url_kwarg = 'slug'
    limit_choices_to = models.Q()

    def get_context(self, request, **kwargs):
        assert self.lookup_url_kwarg in kwargs
        filter_kwargs = {self.lookup_field: kwargs.pop(self.lookup_url_kwarg)}
        if hasattr(self.product_model, 'translations'):
            filter_kwargs.update(translations__language_code=get_language_from_request(self.request))
        queryset = self.product_model.objects.filter(self.limit_choices_to, **filter_kwargs)
        product = get_object_or_404(queryset)
        return {'product': product, 'request': request}

    def get(self, request, *args, **kwargs):
        context = self.get_context(request, **kwargs)
        serializer = self.serializer_class(context=context, **kwargs)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        context = self.get_context(request, **kwargs)
        serializer = self.serializer_class(data=request.data, context=context)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductRetrieveView(generics.RetrieveAPIView):
    """
    This view is used to retrieve and render a certain product.

    Usage: Add it to the urlpatterns responsible for rendering the catalog's views. The
    file containing this patterns can be referenced by the CMS apphook ``CatalogListCMSApp``
    and used by the CMS pages responsible for rendering the catalog's list.
    ```
    urlpatterns = [
        ...
        url(r'^(?P<slug>[\w-]+)', ProductRetrieveView.as_view()),
        url(r'^', ProductListView.as_view()),  # see above
    ]
    ```
    You may add these attributes to the ``as_view()`` method:

    :param renderer_classes: A list or tuple of REST renderer classes.

    :param lookup_field: The model field used to retrieve the product instance.

    :param lookup_url_kwarg: The name of the parsed URL fragment.

    :param serializer_class: The serializer class used to process the queryset returned
        by the catalog's product detail view.

    :param limit_choices_to: Limit the queryset of product models to these choices.

    :param use_modal_dialog: If ``True`` (default), render a modal dialog to confirm adding the
        product to the cart.
    """

    renderer_classes = (ShopTemplateHTMLRenderer, JSONRenderer, BrowsableAPIRenderer)
    lookup_field = lookup_url_kwarg = 'slug'
    product_model = ProductModel
    serializer_class = ProductSerializer
    limit_choices_to = models.Q()
    use_modal_dialog = True

    def dispatch(self, request, *args, **kwargs):
        """
        In some Shop configurations, it is common to render the the catalog's list view right on
        the main landing page. Therefore we have a combination of the ``ProductListView`` and the
        ``ProductRetrieveView`` interfering with the CMS's root page, which means that we have
        overlapping namespaces. For example, the URL ``/awesome-toy`` must be served by the
        ``ProductRetrieveView``, but ``/cart`` is served by **django-CMS**.

        In such a situation, the CMS is not able to intercept all requests intended for itself.
        Instead this ``ProductRetrieveView`` would not find a product if we query for, say
        ``/cart``, and hence would raise a Not Found exception. However, since we have overlapping
        namespaces, this method first attempts to resolve by product, and if that fails, it
        forwards the request to django-CMS.
        """
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            if request.current_page.node.is_root():
                return details(request, kwargs.get('slug'))
            raise
        except:
            raise

    def get_template_names(self):
        product = self.get_object()
        app_label = product._meta.app_label.lower()
        basename = '{}-detail.html'.format(product._meta.model_name)
        return [
            os.path.join(app_label, 'catalog', basename),
            os.path.join(app_label, 'catalog/product-detail.html'),
            'shop/catalog/product-detail.html',
        ]

    def get_renderer_context(self):
        renderer_context = super().get_renderer_context()
        if renderer_context['request'].accepted_renderer.format == 'html':
            # add the product as Python object to the context
            product = self.get_object()
            renderer_context.update(
                app_label=product._meta.app_label.lower(),
                product=product,
                use_modal_dialog=self.use_modal_dialog,
            )
        return renderer_context

    def get_object(self):
        if not hasattr(self, '_product'):
            assert self.lookup_url_kwarg in self.kwargs
            filter_kwargs = {
                'active': True,
                self.lookup_field: self.kwargs[self.lookup_url_kwarg],
            }
            if hasattr(self.product_model, 'translations'):
                filter_kwargs.update(translations__language_code=get_language_from_request(self.request))
            queryset = self.product_model.objects.filter(self.limit_choices_to, **filter_kwargs)
            self._product = get_object_or_404(queryset)
        return self._product


class OnePageResultsSetPagination(pagination.PageNumberPagination):
    def __init__(self):
        self.page_size = ProductModel.objects.count()


class ProductSelectView(generics.ListAPIView):
    """
    A simple list view, which is used only by the admin backend. It is required to fetch
    the data for rendering the select widget when looking up for a product.
    """
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)
    serializer_class = app_settings.PRODUCT_SELECT_SERIALIZER
    pagination_class = OnePageResultsSetPagination

    def get_queryset(self):
        term = self.request.GET.get('term', '')
        if len(term) >= 2:
            return ProductModel.objects.select_lookup(term)
        return ProductModel.objects.all()


class AddFilterContextMixin:
    """
    A mixin to enrich the render context by ``filter`` containing information
    on how to render the filter set, supplied by attribute ``filter_class``.
    """
    def get_renderer_context(self):
        renderer_context = super().get_renderer_context()
        if self.filter_class and renderer_context['request'].accepted_renderer.format == 'html':
            # restrict filter set to products associated to this CMS page only
            queryset = self.product_model.objects.filter(self.limit_choices_to)
            queryset = CMSPagesFilterBackend().filter_queryset(self.request, queryset, self)
            renderer_context['filter'] = self.filter_class.get_render_context(self.request, queryset)
        return renderer_context
