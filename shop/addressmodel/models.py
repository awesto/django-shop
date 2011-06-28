# -*- coding: utf-8 -*-
"""
Holds all the information relevant to the client (addresses for instance)
"""
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from django.conf import settings

BASE_ADDRESS_TEMPLATE = \
_("""
Name: %s,
Address: %s,
Zip-Code: %s,
City: %s,
State: %s,
Country: %s
""")

ADDRESS_TEMPLATE = getattr(settings, 'SHOP_ADDRESS_TEMPLATE', BASE_ADDRESS_TEMPLATE)

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
    
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255,blank=True)
    zip_code = models.CharField(max_length=20)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=255)
    country = models.ForeignKey(Country, blank=True, null=True)
    
    class Meta(object):
        verbose_name = _('Address')
        verbose_name_plural = _("Addresses")

    def clone(self):
        new_kwargs = dict([(fld.name, getattr(self, fld.name)) for fld in self._meta.fields if fld.name != 'id'])
        return self.__class__.objects.create(**new_kwargs)

    def as_text(self):
        return ADDRESS_TEMPLATE % (self.name, '%s\n%s' % (self.address, self.address2),
                                   self.city, self.zip_code, self.state, self.country)
