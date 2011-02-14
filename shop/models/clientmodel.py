# -*- coding: utf-8 -*-
'''
Holds all the information relevant to the client (addresses for instance)
'''
from django.contrib.auth.models import User
from django.db import models

class Client(models.Model):
    user = models.OneToOneField(User, related_name="client")
    
    date_of_birth = models.DateField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'shop'
    
    def __unicode__(self):
        return "ClientProfile for %s %s" % (self.user.first_name, self.user.last_name)
    
    #@property
    def shipping_address(self):
        return Address.objects.filter(client=self).filter(is_shipping=True)[0]
    
    #@property
    def billing_address(self):
        return Address.objects.filter(client=self).filter(is_billing=True)[0]
    
    

class Country(models.Model):
    name = models.CharField(max_length=255)
    
    class Meta:
        app_label = 'shop'
        verbose_name_plural = "countries"

class Address(models.Model):
    client = models.ForeignKey(Client, related_name="addresses")
    
    address = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=20)
    state = models.CharField(max_length=255)
    country = models.ForeignKey(Country)
    
    is_shipping = models.BooleanField() # Is it the default shipping address?
    is_billing = models.BooleanField() # is it the default billing address? 
    
    class Meta:
        app_label = 'shop'
        