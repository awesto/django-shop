from django.conf import settings
from django.template.loader import select_template
from django.utils import translation
from django.utils.html import strip_spaces_between_tags
from django.utils.safestring import mark_safe
# from haystack import indexes

from elasticsearch_dsl import analyzer
from django_elasticsearch_dsl import Document, Index, fields
from django_elasticsearch_dsl.fields import TextField
from django_elasticsearch_dsl.registries import registry

from shop.models.product import ProductModel


# class ProductIndex(indexes.SearchIndex):
#     """
#     Abstract base class used to index all products for this shop
#     """
#     text = indexes.CharField(document=True, use_template=True)
#     autocomplete = indexes.EdgeNgramField(use_template=True)
#     product_name = indexes.CharField(stored=True, indexed=False, model_attr='product_name')
#     product_url = indexes.CharField(stored=True, indexed=False, model_attr='get_absolute_url')
#     categories = indexes.MultiValueField(stored=True, indexed=False)
#
#     def get_model(self):
#         """
#         Hook to refer to the used Product model. Override this to create indices of
#         specialized product models.
#         """
#         return ProductModel
#
#     def prepare(self, product):
#         if hasattr(product, 'translations'):
#             product.set_current_language(self.language)
#         with translation.override(self.language):
#             data = super(ProductIndex, self).prepare(product)
#         return data
#
#     def prepare_categories(self, product):
#         category_fields = getattr(product, 'category_fields', [])
#         category_ids = set(page.pk for field in category_fields for page in getattr(product, field).all())
#         return category_ids
#
#     def render_html(self, prefix, product, postfix):
#         """
#         Render a HTML snippet to be stored inside the index database, so that rendering of the
#         product's list views can be performed without database queries.
#         """
#         app_label = product._meta.app_label.lower()
#         params = [
#             (app_label, prefix, product.product_model, postfix),
#             (app_label, prefix, 'product', postfix),
#             ('shop', prefix, 'product', postfix),
#         ]
#         template = select_template(['{0}/products/{1}-{2}-{3}.html'.format(*p) for p in params])
#         context = {'product': product}
#         content = strip_spaces_between_tags(template.render(context).strip())
#         return mark_safe(content)
#
#     def index_queryset(self, using=None):
#         """Used when the entire index for model is updated."""
#         if using in dict(settings.LANGUAGES):
#             self.language = using
#         else:
#             self.language = settings.LANGUAGE_CODE
#         return self.get_model().objects.indexable()


html_strip = analyzer(
    'html_strip',
    tokenizer="standard",
    filter=["standard", "lowercase", "stop", "snowball"],
    char_filter=["html_strip"]
)


class ProductDocument(Document):
    caption = fields.TextField()

    catalog_media = fields.TextField(
        index=False,
    )

    search_media = fields.TextField(
        index=False,
    )

    product_url = fields.KeywordField(
        index=False,
        attr='get_absolute_url',
    )

    class Django:
        model = ProductModel
        fields = ['id', 'product_name']

    # description = fields.TextField(
    #     analyzer=html_strip,
    #     fields={
    #         'raw': fields.TextField(analyzer='keyword'),
    #     }
    # )
    # class Index:
    #     name = 'products'
    #     settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(active=True)

    def prepare_caption(self, instance):
        return instance.caption

    def prepare_catalog_media(self, product):
        return self.render_html('catalog', product, 'media')

    def prepare_search_media(self, product):
        return self.render_html('search', product, 'media')

    def render_html(self, prefix, product, postfix):
        """
        Render a HTML snippet to be stored inside the index database, so that rendering of the
        product's list views can be performed without database queries.
        """
        app_label = product._meta.app_label.lower()
        params = [
            (app_label, prefix, product.product_model, postfix),
            (app_label, prefix, 'product', postfix),
            ('shop', prefix, 'product', postfix),
        ]
        template = select_template(['{0}/products/{1}-{2}-{3}.html'.format(*p) for p in params])
        context = {'product': product}
        content = strip_spaces_between_tags(template.render(context).strip())
        return mark_safe(content)

