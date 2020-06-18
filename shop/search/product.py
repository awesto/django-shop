from elasticsearch_dsl.document import Document
from elasticsearch_dsl.field import Text, Keyword


class BaseProduct(Document):
    url = Keyword(required=True)

    language = Keyword(
        required=False,
    )

    product_codes = Keyword(
        multi=True,
        boost=3,
    )

    product_name = Text(
        boost=2,
    )

    product_type = Keyword()
