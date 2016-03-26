# -*- coding: utf-8 -*-
import copy
from django.core.exceptions import ImproperlyConfigured
from django.db.models.base import ModelBase
from django.db import models
from django.utils import six
from django.utils.functional import SimpleLazyObject, empty
from shop import settings as shop_settings


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
            app_label = shop_settings.APP_LABEL

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
                elif isinstance(baseclass, cls):
                    cls._materialized_models[basename] = Model.__name__
                    # remember the materialized model mapping in the base class for further usage
                    baseclass._materialized_model = Model
            cls.process_pending_mappings(Model, basename)

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
        Model.perform_model_checks()
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
        if key == '_materialized_model':
            msg = "No class implements abstract base model: `{}`."
            raise ImproperlyConfigured(msg.format(self.__name__))
        return object.__getattribute__(self, key)

    @classmethod
    def perform_model_checks(cls):
        """
        Hook for each class inheriting from ForeignKeyBuilder, to perform checks on the
        implementation of the just created class type.
        """


class MaterializedModel(SimpleLazyObject):
    """
    Wrap the base model into a lazy object, so that we can refer to members of its
    materialized model using lazy evaluation.
    """
    def __init__(self, base_model):
        self.__dict__['_base_model'] = base_model
        super(SimpleLazyObject, self).__init__()

    def _setup(self):
        self._wrapped = getattr(self._base_model, '_materialized_model')

    def __call__(self, *args, **kwargs):
        # calls the constructor of the materialized model
        if self._wrapped is empty:
            self._setup()
        return self._wrapped(*args, **kwargs)

    def __deepcopy__(self, memo):
        if self._wrapped is empty:
            # We have to use SimpleLazyObject, not self.__class__, because the latter is proxied.
            result = MaterializedModel(self._base_model)
            memo[id(self)] = result
            return result
        else:
            return copy.deepcopy(self._wrapped, memo)

    def __repr__(self):
        if self._wrapped is empty:
            repr_attr = self._base_model
        else:
            repr_attr = self._wrapped
        return '<MaterializedModel: {}>'.format(repr_attr)

    def __instancecheck__(self, instance):
        if self._wrapped is empty:
            self._setup()
        return isinstance(instance, self._materialized_model)
