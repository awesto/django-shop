from rest_framework import generics
from shop.views.catalog import ProductRetrieveView
from myshop.models.i18n_polymorphic.smartcard import SmartCard
from myshop.serializers.polymorphic import SmartCardSerializer


class MyProductDetailView(generics.mixins.UpdateModelMixin, ProductRetrieveView):
    def get_renderer_context(self):
        renderer_context = super(MyProductDetailView, self).get_renderer_context()
        renderer_context.update(serializer=self.get_serializer(renderer_context['product']))
        return renderer_context

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get_serializer(self, instance, *args, **kwargs):
        if isinstance(instance, SmartCard):
            serializer_class = SmartCardSerializer
        else:
            serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(instance, *args, **kwargs)
