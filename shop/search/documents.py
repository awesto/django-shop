# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.template.loader import select_template

from django_elasticsearch_dsl import fields, Document
from elasticsearch_dsl import analyzer

from shop.models.product import ProductModel


html_strip = analyzer(
    'html_strip',
    tokenizer='standard',
    filter=['lowercase', 'stop', 'snowball'],
    char_filter=['html_strip'],
)


class ProductDocument(Document):
    product_code = fields.KeywordField(
        multi=True,
        boost=5,
    )

    product_name = fields.TextField(
        boost=3,
    )

    product_type = fields.TextField()

    body = fields.TextField(
        analyzer=html_strip,
    )

    class Django:
        model = ProductModel
        fields = ['id']

    def __str__(self):
        return "{} {}: {}".format(self.product_type, self.id, self.product_name)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(active=True)

    def prepare_product_code(self, instance):
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
        print(f"------------ {instance.id}: {instance.product_model}")
        app_label = instance._meta.app_label.lower()
        params = [
            (app_label, instance.product_model),
            (app_label, 'product'),
            ('shop', 'product'),
        ]
        template = select_template(['{0}/search/indexes/{1}.txt'.format(*p) for p in params])
        body = template.render({'product': instance})
        print(body)
        return body
