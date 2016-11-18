# -*- coding: utf-8 -*-
from __future__ import unicode_literals


def get_registered_serializer_class(name):
    from shop.rest.serializers import RegistryMetaclass
    return RegistryMetaclass.get_serializer_class(name)
