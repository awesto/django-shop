"""
Override django.core.serializers.json.Serializer which renders our MoneyType as float.
"""
import json
from django.core.serializers.json import DjangoJSONEncoder, Serializer as DjangoSerializer
from django.core.serializers.json import Deserializer
from shop.money.money_maker import AbstractMoney


__all__ = ['JSONEncoder', 'Serializer', 'Deserializer']


class JSONEncoder(DjangoJSONEncoder):
    """
    Money type aware JSON encoder for reciprocal usage, such as import/export/dumpdata/loaddata.
    """
    def default(self, obj):
        if isinstance(obj, AbstractMoney):
            return float(obj)
        return super().default(obj)


class Serializer(DjangoSerializer):
    """
    Money type aware JSON serializer.
    """
    def end_object(self, obj):
        # self._current has the field data
        indent = self.options.get("indent")
        if not self.first:
            self.stream.write(",")
            if not indent:
                self.stream.write(" ")
        if indent:
            self.stream.write("\n")
        kwargs = dict(self.json_kwargs, cls=JSONEncoder)
        json.dump(self.get_dump_object(obj), self.stream, **kwargs)
        self._current = None
