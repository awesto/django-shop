from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject
from django.utils import timezone

from shop.models.customer import CustomerModel


def get_customer(request, force=False):
    if force or not hasattr(request, '_cached_customer'):
        request._cached_customer = CustomerModel.objects.get_from_request(request)
    return request._cached_customer


class CustomerMiddleware(MiddlewareMixin):
    """
    Similar to Django's AuthenticationMiddleware, which adds the user object to the request,
    this middleware adds the customer object to the request.
    """
    def process_request(self, request):
        assert hasattr(request, 'session'), (
            "The django-SHOP middleware requires session middleware to be installed. "
            "Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'.")
        assert hasattr(request, 'user'), (
            "The django-SHOP middleware requires an authentication middleware to be installed. "
            "Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.auth.middleware.AuthenticationMiddleware'.")
        request.customer = SimpleLazyObject(lambda: get_customer(request))

    def process_response(self, request, response):
        content_type = response.get('content-type')
        try:
            if content_type.startswith('text/html'):
                # only update last_access when rendering the main page
                request.customer.last_access = timezone.now()
                request.customer.save(update_fields=['last_access'])
        except (AttributeError, ValueError):
            pass
        return response
