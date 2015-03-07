# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.models.base import ModelBase
from django.db import models
from django.utils import six


class DeferredRelatedField(object):
    def __init__(self, to, **kwargs):
        try:
            self.abstract_model = to._meta.object_name
        except AttributeError:
            assert isinstance(to, six.string_types), "%s(%r) is invalid. First parameter must be either a model or a model name" % (self.__class__.__name__, to)
            self.abstract_model = to
        else:
            assert to._meta.abstract, "%s can only define a relation with abstract class %s" % (self.__class__.__name__, to._meta.object_name)
        self.options = kwargs


class OneToOneField(DeferredRelatedField):
    """
    Use this class to specify a one-to-one key in abstract classes. It will be converted into a real
    ``OneToOneField`` whenever a real model class is derived from a given abstract class.
    """
    MaterializedField = models.OneToOneField


class ForeignKey(DeferredRelatedField):
    """
    Use this class to specify foreign keys in abstract classes. It will be converted into a real
    ``ForeignKey`` whenever a real model class is derived from a given abstract class.
    """
    MaterializedField = models.ForeignKey


class ManyToManyField(DeferredRelatedField):
    """
    Use this class to specify many-to-many keys in abstract classes. They will be converted into a
    real ``ManyToManyField`` whenever a real model class is derived from a given abstract class.
    """
    MaterializedField = models.ManyToManyField


class ForeignKeyBuilder(ModelBase):
    """
    Here the magic happens: All known and deferred foreign keys are mapped to their correct model's
    counterpart.
    If the main application stores its models in its own directory, add to settings.py:
    SHOP_APP_LABEL = 'myshop'
    so that the models are created inside your own shop instatiation.
    """
    _materialized_models = {}
    _pending_mappings = []

    def __new__(cls, name, bases, attrs):
        class Meta:
            app_label = getattr(settings, 'SHOP_APP_LABEL', 'shop')

        attrs.setdefault('Meta', Meta)
        if not hasattr(attrs['Meta'], 'app_label') and not getattr(attrs['Meta'], 'abstract', False):
            attrs['Meta'].app_label = Meta.app_label
        attrs.setdefault('__module__', getattr(bases[-1], '__module__'))
        Model = super(ForeignKeyBuilder, cls).__new__(cls, name, bases, attrs)
        if Model._meta.abstract:
            return Model
        for baseclass in bases:
            # classes which materialize an abstract model are added to a mapping dictionary
            basename = baseclass.__name__
            try:
                if not issubclass(Model, baseclass) or not baseclass._meta.abstract:
                    raise ImproperlyConfigured("Base class %s is not abstract." % basename)
            except (AttributeError, NotImplementedError):
                pass
            else:
                if basename in cls._materialized_models:
                    if Model.__name__ != cls._materialized_models[basename]:
                        raise AssertionError("Both Model classes '%s' and '%s' inherited from abstract"
                            "base class %s, which is disallowed in this configuration." %
                            (Model.__name__, cls._materialized_models[basename], basename))
                else:
                    cls._materialized_models[basename] = Model.__name__
                    # remember the materialized model mapping in the base class for further usage
                    baseclass.MaterializedModel = Model
            ForeignKeyBuilder.process_pending_mappings(Model, basename)

        # search for deferred foreign fields in our Model
        for attrname in dir(Model):
            try:
                member = getattr(Model, attrname)
            except AttributeError:
                continue
            if not isinstance(member, DeferredRelatedField):
                continue
            mapmodel = cls._materialized_models.get(member.abstract_model)
            if mapmodel:
                field = member.MaterializedField(mapmodel, **member.options)
                field.contribute_to_class(Model, attrname)
            else:
                ForeignKeyBuilder._pending_mappings.append((Model, attrname, member,))
        return Model

    @staticmethod
    def process_pending_mappings(Model, basename):
        # check for pending mappings and in case, process them and remove them from the list
        for mapping in ForeignKeyBuilder._pending_mappings[:]:
            if mapping[2].abstract_model == basename:
                field = mapping[2].MaterializedField(Model, **mapping[2].options)
                field.contribute_to_class(mapping[0], mapping[1])
                ForeignKeyBuilder._pending_mappings.remove(mapping)

    def __getattr__(self, key):
        if key == 'MaterializedModel':
            msg = "No class implements abstract base model: `{}`"
            raise ImproperlyConfigured(msg.format(self.__name__))
        return object.__getattribute__(self, key)
