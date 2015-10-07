# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from decimal import Decimal
import cPickle as pickle
from django.utils.formats import number_format
from . import Money
from .money_maker import MoneyMaker, AbstractMoney

# Tests:
m1 = Money('1.46')
m2 = Money('3.54')
m3 = Money(Decimal('8.99'))
m4 = Money(m3)
num = Decimal(3)

print m1 > 0

nan = Money()
print nan
print repr(nan)
print nan + m1
print m1 + nan
print m2 - nan
print nan - m3
m4 = 100 * m1
print int(m1)

pickled = pickle.dumps(m4)
m5 = pickle.loads(pickled)
assert m4 == m5

print MoneyMaker('JPY')(99)
#print AbstractMoney('3.55')

print repr(m2)

print m1 + m2
print float(m2)
print '{:f}'.format(m2)

print number_format(m1)
print num * m1
print m2 * num

print str(m1)
print m1 - m2
print m1 * num
print num * m2
print m1 / num
m1 += m2
print m1

m3 = -m2
print m3
print Decimal(m3)

p1 = MoneyMaker('GBP')('7.77')
p2 = MoneyMaker('GBP')('1.44')
print repr(p2)
print p1 + p2


z = 0
print m1 + z
print z + m1
