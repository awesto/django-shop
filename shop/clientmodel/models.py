# -*- coding: utf-8 -*-
"""
Holds all the information relevant to the client (addresses for instance)
"""
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

class Client(models.Model):
    user = models.OneToOneField(User, related_name="client")
    
    date_of_birth = models.DateField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta(object):
        verbose_name = _('Client')
        verbose_name_plural = _('Clients')

    def __unicode__(self):
        return "ClientProfile for %s %s" % (self.user.first_name, self.user.last_name)
    
    def shipping_address(self):
        return Address.objects.filter(client=self).filter(is_shipping=True)[0]
    
    def billing_address(self):
        return Address.objects.filter(client=self).filter(is_billing=True)[0]
    
    

class Country(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return u'%s' % self.name
    
    class Meta(object):
        verbose_name = _('Country')
        verbose_name_plural = _('Coutries')


class Address(models.Model):
    #client = models.ForeignKey(Client, related_name="addresses")
    
    user_shipping = models.OneToOneField(User, related_name='shipping_address', blank=True, null=True)
    user_billing = models.OneToOneField(User, related_name='billing_address', blank=True, null=True)
    
    address = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255,blank=True)
    zip_code = models.CharField(max_length=20)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=255)
    country = models.ForeignKey(Country, blank=True, null=True)
    
    #is_shipping = models.BooleanField() # Is it the default shipping address?
    #is_billing = models.BooleanField() # is it the default billing address? 
    
    class Meta:
        verbose_name_plural = "addresses"
        
