# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from shop.models.customer import CustomerModel


def customer(request):
    """
    Add the customer to the RequestContext
    """
    assert hasattr(request, 'customer'), "The request object does not contain a customer. Edit your MIDDLEWARE_CLASSES setting to insert 'shop.middlerware.CustomerMiddleware'."

    context = {'customer': request.customer}
    if request.user.is_staff:
        try:
            context.update(customer=CustomerModel.objects.get(pk=request.session['emulate_user_id']))
        except (CustomerModel.DoesNotExist, KeyError):
            pass
    return context
