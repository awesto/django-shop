#-*- coding: utf-8 -*-
from django.conf import settings
from django.core import exceptions
from django.utils.importlib import import_module

CLASS_PATH_ERROR = '''django-shop is unable to interpret settings value for %s. %s should ' \
                   'be in ther form of a tuple: (\'path.to.models.Class\',
                   \'app_label\').''' 

def load_class(class_path, setting_name=None):
    """
    Loads a class given a class_path.  The setting value may be a string or a tuple.
    The setting_name parameter is only there for pretty error output, and 
    therefore is optional
    """
    if isinstance(class_path, basestring):
        pass
    else:
        try:
            class_path, app_label = class_path
        except:
            if setting_name:
                raise exceptions.ImproperlyConfigured(CLASS_PATH_ERROR % (setting_name, setting_name))
            else:
                raise exceptions.ImproperlyConfigured(CLASS_PATH_ERROR % ("this setting", "It"))

    try:
        class_module, class_name = class_path.rsplit('.', 1)
    except ValueError:
        if setting_name:
            txt = '%s isn\'t a valid module. Check your %s setting' % (
                class_path, setting_name)
        else:
            txt = '%s isn\'t a valid module.' % class_path
        raise exceptions.ImproperlyConfigured(txt)

    try:
        mod = import_module(class_module)
    except ImportError, e:
        if setting_name:
            txt = 'Error importing backend %s: "%s". Check your %s setting' % (
                class_module, e, setting_name)
        else:
            txt = 'Error importing backend %s: "%s".' % (class_module, e)
        raise exceptions.ImproperlyConfigured(txt)

    try:
        clazz = getattr(mod, class_name)
    except AttributeError:
        if setting_name:
            txt = ('Backend module "%s" does not define a "%s" class. Check'
                   ' your %s setting' % (class_module, class_name,
                       setting_name))
        else:
            txt = 'Backend module "%s" does not define a "%s" class.' % (
                class_module, class_name)
        raise exceptions.ImproperlyConfigured(txt)
    return clazz


def get_model_string(model_name):
    """
    Returns the model string notation Django uses for lazily loaded ForeignKeys
    (eg 'auth.User') to prevent circular imports.

    This is needed to allow our crazy custom model usage.
    """
    setting_name = 'SHOP_%s_MODEL' % model_name.upper().replace('_', '')
    class_path = getattr(settings, setting_name, None)
        
    if not class_path:
        return 'shop.%s' % model_name
    elif isinstance(class_path, basestring):
        parts = class_path.split('.')
        try:
            index = parts.index('models') - 1
        except ValueError, e:
            raise exceptions.ImproperlyConfigured(CLASS_PATH_ERROR % (setting_name, setting_name))
        app_label, model_name = parts[index], parts[-1]
    else:
        try:
            class_path, app_label = class_path
            model_name = class_path.split('.')[-1]
        except:
            raise exceptions.ImproperlyConfigured(CLASS_PATH_ERROR % (setting_name, setting_name))

    return "%s.%s" % (app_label, model_name)

