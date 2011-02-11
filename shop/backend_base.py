#-*- coding: utf-8 -*-
from shop.models.ordermodel import Order


class BaseBackendAPI(object):
    def getOrder(self, request):
        '''
        Returns the order object for the current shopper.
        
        This is called from the backend's views as: 
        >>> order = self.shop.getOrder(request)
        '''
        user = request.user
        order = Order.objects.filter(user=user).filter(status=Order.CONFIRMED)
        return order

class BaseBackend(object):
    def __init__(self):
        '''
        This enforces having a valid name and url namespace defined, as well as
        having a proper shop backend defined.
        '''
        if self.backend_name == "":
            raise NotImplementedError(
                'One of your payment backends lacks a name, please define one.')
        if self.url_namespace == "":
            raise NotImplementedError(
                'Please set a namespace for backend "%s"' % self.backend_name)