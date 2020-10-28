from cms.utils import get_current_site
from cms.utils.page import get_page_from_path
from django.urls import reverse
from filer.models.imagemodels import Image
from rest_framework import serializers


class CMSPagesField(serializers.Field):
    """
    A serializer field used to create the many-to-many relations for models inheriting from the
    unmanaged :class:`shop.models.related.BaseProductPage`.

    Usage in serializers to import/export product model data:

    class MyProductSerializer():
        ...
        cms_pages = CMSPagesField()
        ...
    """
    def to_representation(self, value):
        urls = {page.get_absolute_url() for page in value.all()}
        return list(urls)

    def to_internal_value(self, data):
        site = get_current_site()
        pages_root = reverse('pages-root')
        ret = []
        for path in data:
            if path.startswith(pages_root):
                path = path[len(pages_root):]
            # strip any final slash
            if path.endswith('/'):
                path = path[:-1]
            page = get_page_from_path(site, path)
            if page:
                ret.append(page)
        return ret


class ImagesField(serializers.Field):
    """
    A serializer field used to create the many-to-many relations for models inheriting from the
    unmanaged :class:`shop.models.related.BaseProductImage`.

    Usage in serializers to import/export product model data:

    class MyProductSerializer():
        ...
        images = ImagesField()
        ...
    """
    def to_representation(self, value):
        return list(value.values_list('pk', flat=True))

    def to_internal_value(self, data):
        return list(Image.objects.filter(pk__in=data))


class ValueRelatedField(serializers.RelatedField):
    """
    A serializer field used to access a single value from a related model.
    Usage:

        myfield = ValueRelatedField(model=MyModel)
        myfield = ValueRelatedField(model=MyModel, field_name='myfield')

    This serializes objects of type ``MyModel`` so that that the return data is a simple scalar.

    On deserialization it creates an object of type ``MyModel``, if none could be found with the
    given field name.
    """
    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop('model')
        self.related_field_name = kwargs.pop('field_name', 'name')
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        return self.model.objects.all()

    def to_representation(self, value):
        return getattr(value, self.related_field_name)

    def to_internal_value(self, value):
        data = {self.related_field_name: value}
        instance, _ = self.model.objects.get_or_create(**data)
        return instance
