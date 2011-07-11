"""Decorators for the django-shop application."""

def on_method(function_decorator):
    """
    Enables decorators for functions of classes (for example class based views).

    Credits go to: http://www.toddreed.name/content/django-view-class/
    """
    def decorate_method(unbound_method):
        def method_proxy(self, *args, **kwargs):
            def f(*a, **kw):
                return unbound_method(self, *a, **kw)
            return function_decorator(f)(*args, **kwargs)
        return method_proxy
    return decorate_method
