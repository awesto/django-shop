# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils.six import with_metaclass
from jsonfield.fields import JSONField

from . import deferred

SESSION_KEY = 'shop_anonymous_customer'


class BaseCustomerManager(models.Manager):
    def get_customer(self, request, force_unauth=False):
        """
        If authenticated, return User-related Customer or create a new one.
        If anonymous, return Customer referenced in session or create a new one.
        
        Relating Customers on login is done via signals.
        """
        print "MANAGER get_customer"
        print "user: {}".format(request.user)
        if request.user.is_authenticated() and not force_unauth:
            try:
                return request.user.customer
            except CustomerModel.DoesNotExist:
                # if User has no Customer yet, use anonymous one or create one
                try:
                    customer = CustomerModel.objects.get(pk=request.session[SESSION_KEY])
                    assert customer.is_anonymous()
                    customer.user = request.user
                except KeyError:
                    customer = CustomerModel.objects.create(user=request.user)
                customer.save()
                return customer
        try:
            return CustomerModel.objects.get(pk=request.session[SESSION_KEY])
        except KeyError:
            customer = CustomerModel.objects.create()
            customer.save()
            print "session doesn't contain '{}', creating new customer #{}".format(SESSION_KEY, customer.pk)
            request.session[SESSION_KEY] = customer.pk
            return customer
        


@python_2_unicode_compatible
class BaseCustomer(with_metaclass(deferred.ForeignKeyBuilder, models.Model)):
    """
    Base class for shop customers.
    
    Customer is a profile model that extends
    the django User model if a customer is authenticated. On checkout, a User
    object is created for anonymous customers also (with unusable password).
    """
    SALUTATION = (('mrs', _("Mrs.")), ('mr', _("Mr.")))
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True)
    session_key = models.CharField(max_length=40, unique=True, null=True, blank=True, editable=False,
        help_text=_("Anonymous customers are identified by their session key"))
    salutation = models.CharField(max_length=5, choices=SALUTATION)
    is_guest = models.BooleanField(
        _("Customer has guest status"),
        default=False,
        help_text=_("True if the customer has chosen to place an order as a guest")
    )
    extra = JSONField(default={}, editable=False,
        verbose_name=_("Extra information about this customer"))
    creation_date = models.DateTimeField(auto_now_add=True)
    
    objects = BaseCustomerManager()
    
    class Meta:
        abstract = True
    
    def identifier(self):
        if self.user:
            return self.user.__str__()
        return '<anonymous>'
    
    def __str__(self):
        return self.identifier()
    
    # There are three possible auth states:
    def is_anonymous(self):
        """
        Return true if the customer isn't associated with a django User account.
        
        Anonymous customers have accessed the shop, but not registered or placed
        an order.
        """
        return not self.user
    
    def is_guest(self):
        """
        Return true if the customer has chosen to place an order as a guest.
        """
        return self._is_guest
    
    def is_authenticated(self):
        """
        Return true if the customer is registered.
        """
        return not self.is_guest and self.user
    
    def save(self, *args, **kwargs):
        try:
            if self.user.is_staff or self.user.is_superuser:
                self.is_guest = False
        except AttributeError:
            pass
        super(BaseCustomer, self).save(*args, **kwargs)

#class Customer(BaseCustomer):
#    pass

CustomerModel = deferred.MaterializedModel(BaseCustomer)
