from django.template.loader import select_template
from django.utils import translation

from django_elasticsearch_dsl import fields, Document, Index
from elasticsearch.exceptions import NotFoundError

from shop.conf import app_settings
from shop.models.product import ProductModel
from shop.search.analyzers import body_analyzers


class _ProductDocument(Document):
    product_code = fields.KeywordField(
        multi=True,
        boost=3,
    )

    product_name = fields.TextField(
        boost=2,
    )

    product_type = fields.TextField()

    class Django:
        model = ProductModel
        fields = ['id']
        ignore_signals = True  # performed by ProductModel.update_search_index()
        queryset_pagination = 499  # let DRF do the pagination

    def __str__(self):
        return "{} {}: {}".format(self.product_type, self.id, self.product_name)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(active=True)

    def prepare_product_code(self, instance):
        """
        Create a list of textual representation for product codes.
        """
        has_valid_product_code = lambda obj: isinstance(getattr(obj, 'product_code', None), str)
        variants = instance.get_product_variants()
        product_codes = [v.product_code for v in variants if has_valid_product_code(v)]
        if has_valid_product_code(instance):
            product_codes.append(instance.product_code)
        return product_codes

    def prepare_body(self, instance):
        """
        Create a textual representation of the product's instance to be used by Elasticsearch for
        creating a full text search index.
        """
        app_label = instance._meta.app_label.lower()
        params = [
            (app_label, instance.product_model),
            (app_label, 'product'),
            ('shop', 'product'),
        ]
        template = select_template(['{0}/search/indexes/{1}.txt'.format(*p) for p in params])
        body = template.render({'product': instance})
        return body

    def update(self, thing, refresh=None, action='index', parallel=False, **kwargs):
        if isinstance(thing, ProductModel._materialized_model) and thing.active is False:
            try:
                doc = self.get(id=thing.id)
            except NotFoundError:
                pass
            else:
                doc.delete()
        else:
            if self._language:
                with translation.override(self._language):
                    super().update(thing, refresh=None, action='index', parallel=False, **kwargs)
            else:
                super().update(thing, refresh=None, action='index', parallel=False, **kwargs)


class ProductDocument:
    """
    Factory for building an elasticsearch-dsl Document class. This class
    language_analizers needs to be a dictionary using language as a key and analyzer as a value
    language also needs to set if language_analizers is set
    see https://elasticsearch-dsl.readthedocs.io/en/latest/api.html#elasticsearch_dsl.Index.analyzer
    """
    def __new__(cls, language=None, settings=None, language_analizers=None):
        index_name_parts = [app_settings.SHOP_APP_LABEL]
        if language_analizers:
            copy = language_analizers.copy()
            body_analyzers.update(copy) #overrides default language settings
        if language:
            index_name_parts.append(language.lower())
            doc_name = 'ProductDocument{}'.format(language.title())
            analyzer = body_analyzers.get(language, body_analyzers['default'])
        else:
            doc_name = 'ProductDocument'
            analyzer = body_analyzers['default']
        index_name_parts.append('products')
        products_index = Index('.'.join(index_name_parts))
        if settings:
            products_index.settings(**settings)
        attrs = {'_language': language, 'body': fields.TextField(analyzer=analyzer)}
        doc_class = type(doc_name, (_ProductDocument,), attrs)
        products_index.document(doc_class)
        return doc_class
