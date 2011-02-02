'''
Created on Jan 17, 2011

@author: Christopher Glass <christopher.glass@divio.ch>

Holds all the information relevant to the client (addresses for instance)
'''


from django.contrib.auth.models import User
from django.db import models
import datetime

class Client(models.Model):
    user = models.ForeignKey(User)
    
    date_of_birth = models.DateField()
    created = models.DateTimeField(default=datetime.datetime.now)
    
    def __unicode__(self):
        return "ClientProfile for %s %s" % (self.user.first_name, self.user.last_name)
    
    @property
    def shipping_address(self):
        return Address.objects.filter(client=self).filter(is_shipping=True)[0]
    
    @property
    def billing_address(self):
        return Address.objects.filter(client=self).filter(is_billing=True)[0]

class Country(models.Model):
    name = models.CharField(max_length=255)

class Address(models.Model):
    client = models.ForeignKey(Client, name_related="addresses")
    
    address = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=20)
    state = models.CharField(max_length=255)
    country = models.ForeignKey(Country)
    
    is_shipping = models.BooleanField() # Is it the default shipping address?
    is_billing = models.BooleanField() # is it the default billing address? 