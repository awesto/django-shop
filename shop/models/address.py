# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
Holds all the information relevant to the client (addresses for instance)
"""
from six import with_metaclass

from django.db import models
from django.template.loader import select_template
from django.utils.translation import ugettext_lazy as _

from shop import deferred
from shop.conf import app_settings


class AddressManager(models.Manager):
    def get_max_priority(self, customer):
        aggr = self.get_queryset().filter(customer=customer).aggregate(models.Max('priority'))
        priority = aggr['priority__max'] or 0
        return priority

    def get_fallback(self, customer):
        """
        Return a fallback address, whenever the customer has not declared one.
        """
        return self.get_queryset().filter(customer=customer).order_by('priority').last()


class BaseAddress(models.Model):
    customer = deferred.ForeignKey('BaseCustomer')

    priority = models.SmallIntegerField(
        default=0,
        db_index=True,
        help_text=_("Priority for using this address"),
    )

    class Meta:
        abstract = True

    objects = AddressManager()

    def as_text(self):
        """
        Return the address as plain text to be used for printing, etc.
        """
        template_names = [
            '{}/{}-address.txt'.format(app_settings.APP_LABEL, self.address_type),
            '{}/address.txt'.format(app_settings.APP_LABEL),
            'shop/address.txt',
        ]
        template = select_template(template_names)
        return template.render({'address': self})


class BaseShippingAddress(with_metaclass(deferred.ForeignKeyBuilder, BaseAddress)):
    address_type = 'shipping'

    class Meta:
        abstract = True

ShippingAddressModel = deferred.MaterializedModel(BaseShippingAddress)


class BaseBillingAddress(with_metaclass(deferred.ForeignKeyBuilder, BaseAddress)):
    address_type = 'billing'

    class Meta:
        abstract = True

BillingAddressModel = deferred.MaterializedModel(BaseBillingAddress)

ISO_3166_CODES = [
    ('AF', _("Afghanistan")),
    ('AX', _("Aland Islands")),
    ('AL', _("Albania")),
    ('DZ', _("Algeria")),
    ('AS', _("American Samoa")),
    ('AD', _("Andorra")),
    ('AO', _("Angola")),
    ('AI', _("Anguilla")),
    ('AQ', _("Antarctica")),
    ('AG', _("Antigua And Barbuda")),
    ('AR', _("Argentina")),
    ('AM', _("Armenia")),
    ('AW', _("Aruba")),
    ('AU', _("Australia")),
    ('AT', _("Austria")),
    ('AZ', _("Azerbaijan")),
    ('BS', _("Bahamas")),
    ('BH', _("Bahrain")),
    ('BD', _("Bangladesh")),
    ('BB', _("Barbados")),
    ('BY', _("Belarus")),
    ('BE', _("Belgium")),
    ('BZ', _("Belize")),
    ('BJ', _("Benin")),
    ('BM', _("Bermuda")),
    ('BT', _("Bhutan")),
    ('BO', _("Bolivia, Plurinational State Of")),
    ('BQ', _("Bonaire, Saint Eustatius And Saba")),
    ('BA', _("Bosnia And Herzegovina")),
    ('BW', _("Botswana")),
    ('BV', _("Bouvet Island")),
    ('BR', _("Brazil")),
    ('IO', _("British Indian Ocean Territory")),
    ('BN', _("Brunei Darussalam")),
    ('BG', _("Bulgaria")),
    ('BF', _("Burkina Faso")),
    ('BI', _("Burundi")),
    ('KH', _("Cambodia")),
    ('CM', _("Cameroon")),
    ('CA', _("Canada")),
    ('CV', _("Cape Verde")),
    ('KY', _("Cayman Islands")),
    ('CF', _("Central African Republic")),
    ('TD', _("Chad")),
    ('CL', _("Chile")),
    ('CN', _("China")),
    ('CX', _("Christmas Island")),
    ('CC', _("Cocos (Keeling) Islands")),
    ('CO', _("Colombia")),
    ('KM', _("Comoros")),
    ('CG', _("Congo")),
    ('CD', _("Congo, The Democratic Republic Of The")),
    ('CK', _("Cook Islands")),
    ('CR', _("Costa Rica")),
    ('HR', _("Croatia")),
    ('CU', _("Cuba")),
    ('CW', _("Curacao")),
    ('CY', _("Cyprus")),
    ('CZ', _("Czech Republic")),
    ('DK', _("Denmark")),
    ('DJ', _("Djibouti")),
    ('DM', _("Dominica")),
    ('DO', _("Dominican Republic")),
    ('EC', _("Ecuador")),
    ('EG', _("Egypt")),
    ('SV', _("El Salvador")),
    ('GQ', _("Equatorial Guinea")),
    ('ER', _("Eritrea")),
    ('EE', _("Estonia")),
    ('ET', _("Ethiopia")),
    ('FK', _("Falkland Islands (Malvinas)")),
    ('FO', _("Faroe Islands")),
    ('FJ', _("Fiji")),
    ('FI', _("Finland")),
    ('FR', _("France")),
    ('GF', _("French Guiana")),
    ('PF', _("French Polynesia")),
    ('TF', _("French Southern Territories")),
    ('GA', _("Gabon")),
    ('GM', _("Gambia")),
    ('DE', _("Germany")),
    ('GH', _("Ghana")),
    ('GI', _("Gibraltar")),
    ('GR', _("Greece")),
    ('GL', _("Greenland")),
    ('GD', _("Grenada")),
    ('GP', _("Guadeloupe")),
    ('GU', _("Guam")),
    ('GT', _("Guatemala")),
    ('GG', _("Guernsey")),
    ('GN', _("Guinea")),
    ('GW', _("Guinea-Bissau")),
    ('GY', _("Guyana")),
    ('HT', _("Haiti")),
    ('HM', _("Heard Island and McDonald Islands")),
    ('VA', _("Holy See (Vatican City State)")),
    ('HN', _("Honduras")),
    ('HK', _("Hong Kong")),
    ('HU', _("Hungary")),
    ('IS', _("Iceland")),
    ('IN', _("India")),
    ('ID', _("Indonesia")),
    ('IR', _("Iran, Islamic Republic Of")),
    ('IQ', _("Iraq")),
    ('IE', _("Ireland")),
    ('IL', _("Israel")),
    ('IT', _("Italy")),
    ('CI', _("Ivory Coast")),
    ('JM', _("Jamaica")),
    ('JP', _("Japan")),
    ('JE', _("Jersey")),
    ('JO', _("Jordan")),
    ('KZ', _("Kazakhstan")),
    ('KE', _("Kenya")),
    ('KI', _("Kiribati")),
    ('KP', _("Korea, Democratic People's Republic Of")),
    ('KR', _("Korea, Republic Of")),
    ('KS', _("Kosovo")),
    ('KW', _("Kuwait")),
    ('KG', _("Kyrgyzstan")),
    ('LA', _("Lao People's Democratic Republic")),
    ('LV', _("Latvia")),
    ('LB', _("Lebanon")),
    ('LS', _("Lesotho")),
    ('LR', _("Liberia")),
    ('LY', _("Libyan Arab Jamahiriya")),
    ('LI', _("Liechtenstein")),
    ('LT', _("Lithuania")),
    ('LU', _("Luxembourg")),
    ('MO', _("Macao")),
    ('MK', _("Macedonia")),
    ('MG', _("Madagascar")),
    ('MW', _("Malawi")),
    ('MY', _("Malaysia")),
    ('MV', _("Maldives")),
    ('ML', _("Mali")),
    ('ML', _("Malta")),
    ('MH', _("Marshall Islands")),
    ('MQ', _("Martinique")),
    ('MR', _("Mauritania")),
    ('MU', _("Mauritius")),
    ('YT', _("Mayotte")),
    ('MX', _("Mexico")),
    ('FM', _("Micronesia")),
    ('MD', _("Moldova")),
    ('MC', _("Monaco")),
    ('MN', _("Mongolia")),
    ('ME', _("Montenegro")),
    ('MS', _("Montserrat")),
    ('MA', _("Morocco")),
    ('MZ', _("Mozambique")),
    ('MM', _("Myanmar")),
    ('NA', _("Namibia")),
    ('NR', _("Nauru")),
    ('NP', _("Nepal")),
    ('NL', _("Netherlands")),
    ('AN', _("Netherlands Antilles")),
    ('NC', _("New Caledonia")),
    ('NZ', _("New Zealand")),
    ('NI', _("Nicaragua")),
    ('NE', _("Niger")),
    ('NG', _("Nigeria")),
    ('NU', _("Niue")),
    ('NF', _("Norfolk Island")),
    ('MP', _("Northern Mariana Islands")),
    ('NO', _("Norway")),
    ('OM', _("Oman")),
    ('PK', _("Pakistan")),
    ('PW', _("Palau")),
    ('PS', _("Palestinian Territory, Occupied")),
    ('PA', _("Panama")),
    ('PG', _("Papua New Guinea")),
    ('PY', _("Paraguay")),
    ('PE', _("Peru")),
    ('PH', _("Philippines")),
    ('PN', _("Pitcairn")),
    ('PL', _("Poland")),
    ('PT', _("Portugal")),
    ('PR', _("Puerto Rico")),
    ('QA', _("Qatar")),
    ('RE', _("Reunion")),
    ('RO', _("Romania")),
    ('RU', _("Russian Federation")),
    ('RW', _("Rwanda")),
    ('BL', _("Saint Barthelemy")),
    ('SH', _("Saint Helena, Ascension & Tristan Da Cunha")),
    ('KN', _("Saint Kitts and Nevis")),
    ('LC', _("Saint Lucia")),
    ('MF', _("Saint Martin (French Part)")),
    ('PM', _("Saint Pierre and Miquelon")),
    ('VC', _("Saint Vincent And The Grenadines")),
    ('WS', _("Samoa")),
    ('SM', _("San Marino")),
    ('ST', _("Sao Tome And Principe")),
    ('SA', _("Saudi Arabia")),
    ('SN', _("Senegal")),
    ('RS', _("Serbia")),
    ('SC', _("Seychelles")),
    ('SL', _("Sierra Leone")),
    ('SG', _("Singapore")),
    ('SX', _("Sint Maarten (Dutch Part)")),
    ('SK', _("Slovakia")),
    ('SI', _("Slovenia")),
    ('SB', _("Solomon Islands")),
    ('SO', _("Somalia")),
    ('ZA', _("South Africa")),
    ('GS', _("South Georgia And The South Sandwich Islands")),
    ('ES', _("Spain")),
    ('LK', _("Sri Lanka")),
    ('SD', _("Sudan")),
    ('SR', _("Suriname")),
    ('SJ', _("Svalbard And Jan Mayen")),
    ('SZ', _("Swaziland")),
    ('SE', _("Sweden")),
    ('CH', _("Switzerland")),
    ('SY', _("Syrian Arab Republic")),
    ('TW', _("Taiwan")),
    ('TJ', _("Tajikistan")),
    ('TZ', _("Tanzania")),
    ('TH', _("Thailand")),
    ('TL', _("Timor-Leste")),
    ('TG', _("Togo")),
    ('TK', _("Tokelau")),
    ('TO', _("Tonga")),
    ('TT', _("Trinidad and Tobago")),
    ('TN', _("Tunisia")),
    ('TR', _("Turkey")),
    ('TM', _("Turkmenistan")),
    ('TC', _("Turks And Caicos Islands")),
    ('TV', _("Tuvalu")),
    ('UG', _("Uganda")),
    ('UA', _("Ukraine")),
    ('AE', _("United Arab Emirates")),
    ('GB', _("United Kingdom")),
    ('US', _("United States")),
    ('UM', _("United States Minor Outlying Islands")),
    ('UY', _("Uruguay")),
    ('UZ', _("Uzbekistan")),
    ('VU', _("Vanuatu")),
    ('VE', _("Venezuela, Bolivarian Republic Of")),
    ('VN', _("Viet Nam")),
    ('VG', _("Virgin Islands, British")),
    ('VI', _("Virgin Islands, U.S.")),
    ('WF', _("Wallis and Futuna")),
    ('EH', _("Western Sahara")),
    ('YE', _("Yemen")),
    ('ZM', _("Zambia")),
    ('ZW', _("Zimbabwe")),
]

class CountryField(models.CharField):
    """
    This creates a simple input field to choose a country.
    """
    def __init__(self, *args, **kwargs):
        defaults = {
            'max_length': 3,
            'choices': ISO_3166_CODES,
        }
        defaults.update(kwargs)
        super(CountryField, self).__init__(*args, **defaults)

    def deconstruct(self):
        name, path, args, kwargs = super(CountryField, self).deconstruct()
        if kwargs['max_length'] == 3:
            kwargs.pop('max_length')
        if kwargs['choices'] == ISO_3166_CODES:
            kwargs.pop('choices')
        return name, path, args, kwargs
