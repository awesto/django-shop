# -*- coding: utf-8 -*-
from __future__ import unicode_literals


def customer(request):
    """
    Add the customer to the RequestContext
    """
    assert hasattr(request, 'customer'), "The request object does not contain a customer. Edit your MIDDLEWARE_CLASSES setting to insert 'shop.middlerware.CustomerMiddleware'."
    return {
        'customer': request.customer,
    }
