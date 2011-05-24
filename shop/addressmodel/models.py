# -*- coding: utf-8 -*-
"""
Holds all the information relevant to the client (addresses for instance)
"""
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

class Country(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return u'%s' % self.name
    
    class Meta(object):
        verbose_name = _('Country')
        verbose_name_plural = _('Countries')


class Address(models.Model):
    user_shipping = models.OneToOneField(User, related_name='shipping_address', blank=True, null=True)
    user_billing = models.OneToOneField(User, related_name='billing_address', blank=True, null=True)
    
    address = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255,blank=True)
    zip_code = models.CharField(max_length=20)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=255)
    country = models.ForeignKey(Country, blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "addresses"
        
