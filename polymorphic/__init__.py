# -*- coding: utf-8 -*-
"""
Seamless Polymorphic Inheritance for Django Models

Copyright:
This code and affiliated files are (C) by Bert Constantin and individual contributors.
Please see LICENSE and AUTHORS for more information.
"""

from polymorphic_model import PolymorphicModel
from manager import PolymorphicManager
from query import PolymorphicQuerySet
from query_translate import translate_polymorphic_Q_object
from showfields import ShowFieldContent, ShowFieldType, ShowFieldTypeAndContent
from showfields import ShowFields, ShowFieldTypes, ShowFieldsAndTypes # import old names for compatibility


VERSION = (1, 0 , 0, 'beta')

def get_version():
    version = '%s.%s' % VERSION[0:2]
    if VERSION[2]:
        version += '.%s' % VERSION[2]
    if VERSION[3]:
        version += ' %s' % VERSION[3]
    return version