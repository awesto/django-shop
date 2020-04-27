from shop.search.documents import ProductDocument


class SearchViewMixin:
    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            search = ProductDocument.search().source(excludes=['body'])
            search = search.query('multi_match', query=query, fields=self.search_fields, type='bool_prefix')
            queryset = search.to_queryset()
        else:
            queryset = super().get_queryset()
        return queryset


class ProductSearchViewMixin(SearchViewMixin):
    search_fields = ['product_name', 'product_code']

    def get_renderer_context(self):
        renderer_context = super().get_renderer_context()
        if renderer_context['request'].accepted_renderer.format == 'html':
            renderer_context['search_autocomplete'] = True
        return renderer_context


class CatalogSearchViewMixin(SearchViewMixin):
    search_fields = ['product_name', 'product_code', 'body']

    def get_serializer(self, *args, **kwargs):
        kwargs.setdefault('label', 'search')
        return super().get_serializer(*args, **kwargs)
