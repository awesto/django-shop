# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.template.loader import select_template
from django.utils.html import strip_tags

from django_elasticsearch_dsl import fields, Document

from shop.models.product import ProductModel


# products = Index('products')
# products.settings(
#     number_of_shards=1,
#     number_of_replicas=0
# )


# @products.document
class ProductDocument(Document):
    product_codes = fields.KeywordField(
        multi=True,
    )

    product_type = fields.TextField(
        attr='product_type',
    )

    body = fields.TextField()

    class Django:
        model = ProductModel
        fields = ['id', 'product_name']

    def prepare(self, instance):
        data = super().prepare(instance)
        return data

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(active=True)

    def prepare_product_codes(self, instance):
        variants = instance.get_product_variants()
        product_codes = [
            v.product_code for v in variants if isinstance(getattr(v, 'product_code', None), str)
        ]
        if isinstance(getattr(instance, 'product_code', None), str):
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
        print("------------")
        print(strip_tags(body))
        return strip_tags(body)
