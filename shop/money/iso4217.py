from django.utils.translation import gettext_lazy as _

# Dictionary of currency representations:
# key: official ISO 4217 code
# value[0]: numeric representation
# value[1]: number of digits
# value[2]: currency symbol in UTF-8
# value[3]: textual description
CURRENCIES = {
    'AED': ('784', 2, 'د.إ', _('United Arab Emirates dirham')),
    'AUD': ('036', 2, '$', _("Australian Dollar")),
    'BHD': ('048', 3, '.د.ب', _('Bahraini dinar')),
    'BOB': ('068', 2, 'Bs', _('Boliviano')),
    'BRL': ('986', 2, 'R$', _("Brazilian Real")),
    'CAD': ('124', 2, 'C$', _("Canadian Dollar")),
    'CHF': ('756', 2, 'SFr․', _("Swiss Franc")),  # Unicode 8228 as dot to prevent formatting issues
    'CNY': ('156', 2, '¥', _("Chinese Yuan")),
    'CZK': ('203', 2, 'Kč', _("Czech Koruna")),
    'EUR': ('978', 2, '€', _("Euro")),
    'GBP': ('826', 2, '£', _("Pound Sterling")),
    'HKD': ('344', 2, 'HK$', _("Hong Kong Dollar")),
    'HRK': ('191', 2, 'kn', _("Croatian kuna")),
    'HUF': ('348', 0, 'Ft', _("Hungarian Forint")),
    'ILS': ('376', 2, '₪', _("Israeli Sheqel")),
    'INR': ('356', 2, '₹', _("Indian Rupee")),
    'JPY': ('392', 0, '¥', _("Japanese Yen")),
    'KWD': ('414', 3, 'د.ك', _("Kuwaiti Dinar")),
    'OMR': ('512', 3, 'ر.ع.', _('Omani rial')),
    'QAR': ('634', 2, 'ر.ق', _('Qatari riyal')),
    'RUB': ('643', 2, '₽', _("Russian Ruble")),
    'SAR': ('682', 2, 'ر.س', _('Saudi riyal')),
    'TND': ('788', 3, 'TND', _("Tunisian Dinar")),
    'UAH': ('980', 2, '₴', _("Ukrainian Hryvnia")),
    'USD': ('840', 2, '$', _("US Dollar")),
    'SEK': ('752', 2, 'kr', _("Swedish Kronor")),
    'ZAR': ('710', 2, 'R', _("South African Rand")),
    # feel free to add more currencies, alphabetically ordered
}
