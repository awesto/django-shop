from django.utils.translation import get_language_from_request

from django_elasticsearch_dsl.registries import registry

from shop.models.product import ProductModel


class SearchViewMixin:
    def get_document(self, language):
        documents = registry.get_documents([ProductModel])
        try:
            return next(doc for doc in documents if doc._language == language)
        except StopIteration:
            return next(doc for doc in documents if doc._language is None)


class ProductSearchViewMixin(SearchViewMixin):
    """
    Mixin class to be added to the ProductListView to restrict that list to entities matching
    the query string.
    """
    search_fields = ['product_name', 'product_code']

    def get_renderer_context(self):
        renderer_context = super().get_renderer_context()
        if renderer_context['request'].accepted_renderer.format == 'html':
            renderer_context['search_autocomplete'] = True
        return renderer_context

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            language = get_language_from_request(self.request)
            document = self.get_document(language)
            search = document.search().source(excludes=['body'])
            search = search.query('multi_match', query=query, fields=self.search_fields, type='bool_prefix')
            queryset = search.to_queryset()
        else:
            queryset = super().get_queryset()
        return queryset


class CatalogSearchViewMixin(SearchViewMixin):
    """
    Mixin class to be added to the ProductListView in order to create a full-text search.
    """
    search_fields = ['product_name', 'product_code', 'body']

    def get_serializer(self, *args, **kwargs):
        kwargs.setdefault('label', 'search')
        return super().get_serializer(*args, **kwargs)

    def get_queryset(self):
        language = get_language_from_request(self.request)
        document = self.get_document(language)
        query = self.request.GET.get('q')
        search = document.search().source(excludes=['body'])
        if query:
            search = search.query('multi_match', query=query, fields=self.search_fields)
        return search.to_queryset()
