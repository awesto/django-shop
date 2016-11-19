# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
In version 0.10, all serializers from shop.rest.serializers will be moved into this folder.
"""

def get_registered_serializer_class(name):
    from shop.rest.serializers import RegistryMetaclass
    return RegistryMetaclass.get_serializer_class(name)
