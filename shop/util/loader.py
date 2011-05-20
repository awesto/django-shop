#-*- coding: utf-8 -*-
from django.core import exceptions
from django.utils.importlib import import_module

def load_class(class_path, setting_name):
    try:
        class_module, class_name = class_path.rsplit('.', 1)
    except ValueError:
        raise exceptions.ImproperlyConfigured(
            '%s isn\'t a backend module. Check your %s setting' 
            % (class_path,setting_name))
    try:
        mod = import_module(class_module)
    except ImportError, e:
        raise exceptions.ImproperlyConfigured(
                'Error importing backend %s: "%s". Check your %s setting' 
                % (class_module, e, setting_name))
    try:
        clazz = getattr(mod, class_name)
    except AttributeError:
        raise exceptions.ImproperlyConfigured(
            'Backend module "%s" does not define a "%s" class. Check your %s setting' 
            % (class_module, class_name, setting_name))
    return clazz