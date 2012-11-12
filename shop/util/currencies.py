# -*- coding: utf-8 -*-
from decimal import Decimal


class EuroCurrency(Decimal):
    '''This class allows you to work with euro currency
    '''
    def val(self):
        '''Return a Decimal instance for euro currency using 2 decimal
        positions and rounding to next or previous value based on third
        decimal position

        >>> EuroCurrency(12.447).val()
        Decimal('12.45')
        >>> EuroCurrency('12.443').val()
        Decimal('12.44')
        >>> EuroCurrency('12.44').val()
        Decimal('12.44')
        '''
        two_pos = Decimal(10) ** -2
        return Decimal(self).quantize(two_pos)

    def verbose_name(self):
        return 'euro'

    def verbose_name_plural(self):
        return 'euros'

    def get_symbol(self):
        return u'€'

if __name__ == "__main__":
    import doctest
    doctest.testmod()
