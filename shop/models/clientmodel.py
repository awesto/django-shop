'''
Created on Jan 17, 2011

@author: Christopher Glass <christopher.glass@divio.ch>

Holds all the information relevant to the client (addresses for instance)
'''


from django.contrib.auth.models import User
from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=255)

class Address(models.Model):
    user = models.ForeignKey(User)
    
    address = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=20)
    state = models.CharField(max_length=255)
    country = models.ForeignKey(Country)
    
    is_shipping = models.BooleanField() # Is it the default shipping address?
    is_billing = models.BooleanField() # is it the default billing address? 