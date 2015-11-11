# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import shop.payment.defaults
import filer.fields.image
import django_fsm
import jsonfield.fields
import djangocms_text_ckeditor.fields
import cms.models.fields
import django.utils.timezone
from django.conf import settings
import django.core.validators
import shop_stripe.payment


class Migration(migrations.Migration):

    dependencies = [
        ('email_auth', '0002_auto_20151011_1652'),
        ('contenttypes', '0001_initial'),
        ('filer', '0002_auto_20150606_2003'),
        ('cms', '0012_auto_20150607_2207'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('priority_shipping', models.SmallIntegerField(default=None, help_text='Priority of using this address for shipping', null=True)),
                ('priority_billing', models.SmallIntegerField(default=None, help_text='Priority of using this address for invoicing', null=True)),
                ('addressee', models.CharField(max_length=50, verbose_name='Addressee')),
                ('supplement', models.CharField(max_length=50, null=True, verbose_name='Supplement', blank=True)),
                ('street', models.CharField(max_length=50, verbose_name='Street')),
                ('zip_code', models.CharField(max_length=10, verbose_name='ZIP')),
                ('location', models.CharField(max_length=50, verbose_name='Location')),
                ('country', models.CharField(max_length=3, verbose_name='Country', choices=[('AF', 'Afghanistan'), ('AX', 'Aland Islands'), ('AL', 'Albania'), ('DZ', 'Algeria'), ('AS', 'American Samoa'), ('AD', 'Andorra'), ('AO', 'Angola'), ('AI', 'Anguilla'), ('AQ', 'Antarctica'), ('AG', 'Antigua And Barbuda'), ('AR', 'Argentina'), ('AM', 'Armenia'), ('AW', 'Aruba'), ('AU', 'Australia'), ('AT', 'Austria'), ('AZ', 'Azerbaijan'), ('BS', 'Bahamas'), ('BH', 'Bahrain'), ('BD', 'Bangladesh'), ('BB', 'Barbados'), ('BY', 'Belarus'), ('BE', 'Belgium'), ('BZ', 'Belize'), ('BJ', 'Benin'), ('BM', 'Bermuda'), ('BT', 'Bhutan'), ('BO', 'Bolivia, Plurinational State Of'), ('BQ', 'Bonaire, Saint Eustatius And Saba'), ('BA', 'Bosnia And Herzegovina'), ('BW', 'Botswana'), ('BV', 'Bouvet Island'), ('BR', 'Brazil'), ('IO', 'British Indian Ocean Territory'), ('BN', 'Brunei Darussalam'), ('BG', 'Bulgaria'), ('BF', 'Burkina Faso'), ('BI', 'Burundi'), ('KH', 'Cambodia'), ('CM', 'Cameroon'), ('CA', 'Canada'), ('CV', 'Cape Verde'), ('KY', 'Cayman Islands'), ('CF', 'Central African Republic'), ('TD', 'Chad'), ('CL', 'Chile'), ('CN', 'China'), ('CX', 'Christmas Island'), ('CC', 'Cocos (Keeling) Islands'), ('CO', 'Colombia'), ('KM', 'Comoros'), ('CG', 'Congo'), ('CD', 'Congo, The Democratic Republic Of The'), ('CK', 'Cook Islands'), ('CR', 'Costa Rica'), ('HR', 'Croatia'), ('CU', 'Cuba'), ('CW', 'Curacao'), ('CY', 'Cyprus'), ('CZ', 'Czech Republic'), ('DK', 'Denmark'), ('DJ', 'Djibouti'), ('DM', 'Dominica'), ('DO', 'Dominican Republic'), ('EC', 'Ecuador'), ('EG', 'Egypt'), ('SV', 'El Salvador'), ('GQ', 'Equatorial Guinea'), ('ER', 'Eritrea'), ('EE', 'Estonia'), ('ET', 'Ethiopia'), ('FK', 'Falkland Islands (Malvinas)'), ('FO', 'Faroe Islands'), ('FJ', 'Fiji'), ('FI', 'Finland'), ('FR', 'France'), ('GF', 'French Guiana'), ('PF', 'French Polynesia'), ('TF', 'French Southern Territories'), ('GA', 'Gabon'), ('GM', 'Gambia'), ('DE', 'Germany'), ('GH', 'Ghana'), ('GI', 'Gibraltar'), ('GR', 'Greece'), ('GL', 'Greenland'), ('GD', 'Grenada'), ('GP', 'Guadeloupe'), ('GU', 'Guam'), ('GT', 'Guatemala'), ('GG', 'Guernsey'), ('GN', 'Guinea'), ('GW', 'Guinea-Bissau'), ('GY', 'Guyana'), ('HT', 'Haiti'), ('HM', 'Heard Island and McDonald Islands'), ('VA', 'Holy See (Vatican City State)'), ('HN', 'Honduras'), ('HK', 'Hong Kong'), ('HU', 'Hungary'), ('IS', 'Iceland'), ('IN', 'India'), ('ID', 'Indonesia'), ('IR', 'Iran, Islamic Republic Of'), ('IQ', 'Iraq'), ('IE', 'Ireland'), ('IL', 'Israel'), ('IT', 'Italy'), ('CI', 'Ivory Coast'), ('JM', 'Jamaica'), ('JP', 'Japan'), ('JE', 'Jersey'), ('JO', 'Jordan'), ('KZ', 'Kazakhstan'), ('KE', 'Kenya'), ('KI', 'Kiribati'), ('KP', "Korea, Democratic People's Republic Of"), ('KR', 'Korea, Republic Of'), ('KS', 'Kosovo'), ('KW', 'Kuwait'), ('KG', 'Kyrgyzstan'), ('LA', "Lao People's Democratic Republic"), ('LV', 'Latvia'), ('LB', 'Lebanon'), ('LS', 'Lesotho'), ('LR', 'Liberia'), ('LY', 'Libyan Arab Jamahiriya'), ('LI', 'Liechtenstein'), ('LT', 'Lithuania'), ('LU', 'Luxembourg'), ('MO', 'Macao'), ('MK', 'Macedonia'), ('MG', 'Madagascar'), ('MW', 'Malawi'), ('MY', 'Malaysia'), ('MV', 'Maldives'), ('ML', 'Mali'), ('ML', 'Malta'), ('MH', 'Marshall Islands'), ('MQ', 'Martinique'), ('MR', 'Mauritania'), ('MU', 'Mauritius'), ('YT', 'Mayotte'), ('MX', 'Mexico'), ('FM', 'Micronesia'), ('MD', 'Moldova'), ('MC', 'Monaco'), ('MN', 'Mongolia'), ('ME', 'Montenegro'), ('MS', 'Montserrat'), ('MA', 'Morocco'), ('MZ', 'Mozambique'), ('MM', 'Myanmar'), ('NA', 'Namibia'), ('NR', 'Nauru'), ('NP', 'Nepal'), ('NL', 'Netherlands'), ('AN', 'Netherlands Antilles'), ('NC', 'New Caledonia'), ('NZ', 'New Zealand'), ('NI', 'Nicaragua'), ('NE', 'Niger'), ('NG', 'Nigeria'), ('NU', 'Niue'), ('NF', 'Norfolk Island'), ('MP', 'Northern Mariana Islands'), ('NO', 'Norway'), ('OM', 'Oman'), ('PK', 'Pakistan'), ('PW', 'Palau'), ('PS', 'Palestinian Territory, Occupied'), ('PA', 'Panama'), ('PG', 'Papua New Guinea'), ('PY', 'Paraguay'), ('PE', 'Peru'), ('PH', 'Philippines'), ('PN', 'Pitcairn'), ('PL', 'Poland'), ('PT', 'Portugal'), ('PR', 'Puerto Rico'), ('QA', 'Qatar'), ('RE', 'Reunion'), ('RO', 'Romania'), ('RU', 'Russian Federation'), ('RW', 'Rwanda'), ('BL', 'Saint Barthelemy'), ('SH', 'Saint Helena, Ascension & Tristan Da Cunha'), ('KN', 'Saint Kitts and Nevis'), ('LC', 'Saint Lucia'), ('MF', 'Saint Martin (French Part)'), ('PM', 'Saint Pierre and Miquelon'), ('VC', 'Saint Vincent And The Grenadines'), ('WS', 'Samoa'), ('SM', 'San Marino'), ('ST', 'Sao Tome And Principe'), ('SA', 'Saudi Arabia'), ('SN', 'Senegal'), ('RS', 'Serbia'), ('SC', 'Seychelles'), ('SL', 'Sierra Leone'), ('SG', 'Singapore'), ('SX', 'Sint Maarten (Dutch Part)'), ('SK', 'Slovakia'), ('SI', 'Slovenia'), ('SB', 'Solomon Islands'), ('SO', 'Somalia'), ('ZA', 'South Africa'), ('GS', 'South Georgia And The South Sandwich Islands'), ('ES', 'Spain'), ('LK', 'Sri Lanka'), ('SD', 'Sudan'), ('SR', 'Suriname'), ('SJ', 'Svalbard And Jan Mayen'), ('SZ', 'Swaziland'), ('SE', 'Sweden'), ('CH', 'Switzerland'), ('SY', 'Syrian Arab Republic'), ('TW', 'Taiwan'), ('TJ', 'Tajikistan'), ('TZ', 'Tanzania'), ('TH', 'Thailand'), ('TL', 'Timor-Leste'), ('TG', 'Togo'), ('TK', 'Tokelau'), ('TO', 'Tonga'), ('TT', 'Trinidad and Tobago'), ('TN', 'Tunisia'), ('TR', 'Turkey'), ('TM', 'Turkmenistan'), ('TC', 'Turks And Caicos Islands'), ('TV', 'Tuvalu'), ('UG', 'Uganda'), ('UA', 'Ukraine'), ('AE', 'United Arab Emirates'), ('GB', 'United Kingdom'), ('US', 'United States'), ('UM', 'United States Minor Outlying Islands'), ('UY', 'Uruguay'), ('UZ', 'Uzbekistan'), ('VU', 'Vanuatu'), ('VE', 'Venezuela, Bolivarian Republic Of'), ('VN', 'Viet Nam'), ('VG', 'Virgin Islands, British'), ('VI', 'Virgin Islands, U.S.'), ('WF', 'Wallis and Futuna'), ('EH', 'Western Sahara'), ('YE', 'Yemen'), ('ZM', 'Zambia'), ('ZW', 'Zimbabwe')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('extra', jsonfield.fields.JSONField(default={}, verbose_name='Arbitrary information for this cart')),
                ('billing_address', models.ForeignKey(related_name='+', default=None, to='myshop.Address', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('extra', jsonfield.fields.JSONField(default={}, verbose_name='Arbitrary information for this cart item')),
                ('cart', models.ForeignKey(related_name='items', to='myshop.Cart')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('user', models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('recognized', models.PositiveSmallIntegerField(default=0, help_text='Designates the state the customer is recognized as.', verbose_name='Recognized as', choices=[(0, 'Unrecognized'), (1, 'Guest'), (2, 'Registered')])),
                ('salutation', models.CharField(max_length=5, verbose_name='Salutation', choices=[('mrs', 'Mrs.'), ('mr', 'Mr.'), ('na', '(n/a)')])),
                ('last_access', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last accessed')),
                ('extra', jsonfield.fields.JSONField(default={}, verbose_name='Extra information about this customer', editable=False)),
                ('number', models.PositiveIntegerField(default=None, unique=True, null=True, verbose_name='Customer Number')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Manufacturer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OperatingSystem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', django_fsm.FSMField(default='new', protected=True, max_length=50, verbose_name='Status')),
                ('currency', models.CharField(help_text='Currency in which this order was concluded', max_length=7, editable=False)),
                ('_subtotal', models.DecimalField(verbose_name='Subtotal', max_digits=30, decimal_places=2)),
                ('_total', models.DecimalField(verbose_name='Total', max_digits=30, decimal_places=2)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('extra', jsonfield.fields.JSONField(default={}, help_text='Arbitrary information for this order object on the moment of purchase.', verbose_name='Extra fields')),
                ('stored_request', jsonfield.fields.JSONField(default={}, help_text='Parts of the Request objects on the moment of purchase.')),
                ('number', models.PositiveIntegerField(default=None, unique=True, null=True, verbose_name='Order Number')),
                ('shipping_address_text', models.TextField(help_text='Shipping address at the moment of purchase.', null=True, verbose_name='Shipping Address', blank=True)),
                ('billing_address_text', models.TextField(help_text='Billing address at the moment of purchase.', null=True, verbose_name='Billing Address', blank=True)),
                ('customer', models.ForeignKey(related_name='orders', verbose_name='Customer', to='myshop.Customer')),
            ],
            options={
            },
            bases=(shop.payment.defaults.PayInAdvanceWorkflowMixin, shop.payment.defaults.CommissionGoodsWorkflowMixin, shop_stripe.payment.OrderWorkflowMixin, models.Model),
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('product_name', models.CharField(help_text='Product name at the moment of purchase.', max_length=255, null=True, verbose_name='Product name', blank=True)),
                ('product_code', models.CharField(help_text='Product code at the moment of purchase.', max_length=255, null=True, verbose_name='Product code', blank=True)),
                ('_unit_price', models.DecimalField(help_text='Products unit price at the moment of purchase.', null=True, verbose_name='Unit price', max_digits=30, decimal_places=2)),
                ('_line_total', models.DecimalField(help_text='Line total on the invoice at the moment of purchase.', null=True, verbose_name='Line Total', max_digits=30, decimal_places=2)),
                ('quantity', models.IntegerField(verbose_name='Ordered quantity')),
                ('extra', jsonfield.fields.JSONField(default={}, help_text='Arbitrary information for this order item', verbose_name='Extra fields')),
                ('order', models.ForeignKey(related_name='items', verbose_name='Order', to='myshop.Order')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrderPayment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', django_fsm.FSMField(default='new', protected=True, max_length=50, verbose_name='Status')),
                ('amount', models.DecimalField(default='0', help_text='How much was paid with this particular transfer.', max_digits=30, decimal_places=2)),
                ('transaction_id', models.CharField(help_text="The transaction processor's reference", max_length=255, verbose_name='Transaction ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Received at')),
                ('payment_method', models.CharField(help_text='The payment backend used to process the purchase', max_length=255, verbose_name='Payment method')),
                ('order', models.ForeignKey(verbose_name='Order', to='myshop.Order')),
            ],
            options={
                'verbose_name': 'Order payment',
                'verbose_name_plural': 'Order payments',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrderShipping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', django_fsm.FSMField(default='new', protected=True, max_length=50, verbose_name='Status')),
                ('shipping_id', models.CharField(help_text="The transaction processor's reference", max_length=255, verbose_name='Shipping ID')),
                ('shipping_method', models.CharField(help_text='The shipping backend used to deliver the items for this order', max_length=255, verbose_name='Shipping method')),
                ('order', models.ForeignKey(verbose_name='Order', to='myshop.Order')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('active', models.BooleanField(default=True, help_text='Is this product publicly visible.', verbose_name='Active')),
                ('order', models.PositiveIntegerField(verbose_name='Sort by', db_index=True)),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('slug', models.SlugField(verbose_name='Slug')),
            ],
            options={
                'ordering': ('order',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.SmallIntegerField(default=0)),
                ('image', filer.fields.image.FilerImageField(to='filer.Image')),
            ],
            options={
                'ordering': ('order',),
                'verbose_name': 'Product Image',
                'verbose_name_plural': 'Product Images',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProductTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language_code', models.CharField(max_length=15, verbose_name='Language', db_index=True)),
                ('description', djangocms_text_ckeditor.fields.HTMLField(help_text='Description for the list view of products.', verbose_name='Description')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SmartPhone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('product_code', models.CharField(unique=True, max_length=255, verbose_name='Product code')),
                ('unit_price', models.DecimalField(default='0', help_text='Net price for this product', verbose_name='Unit price', max_digits=30, decimal_places=3)),
                ('storage', models.PositiveIntegerField(help_text='Internal storage in MB', verbose_name='Internal Storage')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SmartPhoneModel',
            fields=[
                ('product_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='myshop.Product')),
                ('battery_type', models.PositiveSmallIntegerField(verbose_name='Battery type', choices=[(1, 'Lithium Polymer (Li-Poly)'), (2, 'Lithium Ion (Li-Ion)')])),
                ('battery_capacity', models.PositiveIntegerField(help_text='Battery capacity in mAh', verbose_name='Capacity')),
                ('ram_storage', models.PositiveIntegerField(help_text='RAM storage in MB', verbose_name='RAM')),
                ('wifi_connectivity', models.PositiveIntegerField(help_text='WiFi Connectivity', verbose_name='WiFi', choices=[(1, '802.11 b/g/n')])),
                ('bluetooth', models.PositiveIntegerField(help_text='Bluetooth Connectivity', verbose_name='Bluetooth', choices=[(1, 'Bluetooth 4.0')])),
                ('gps', models.BooleanField(default=False, help_text='GPS integrated', verbose_name='GPS')),
                ('width', models.DecimalField(help_text='Width in mm', verbose_name='Width', max_digits=4, decimal_places=1)),
                ('height', models.DecimalField(help_text='Height in mm', verbose_name='Height', max_digits=4, decimal_places=1)),
                ('weight', models.DecimalField(help_text='Weight in gram', verbose_name='Weight', max_digits=5, decimal_places=1)),
                ('screen_size', models.DecimalField(help_text='Diagonal screen size in inch', verbose_name='Screen size', max_digits=4, decimal_places=2)),
                ('cms_pages', models.ManyToManyField(help_text='Choose list view this phone shall appear on.', to='cms.Page', blank=True)),
                ('manufacturer', models.ForeignKey(verbose_name='Manufacturer', to='myshop.Manufacturer')),
                ('operating_system', models.ForeignKey(verbose_name='Operating System', to='myshop.OperatingSystem')),
            ],
            options={
                'verbose_name': 'Smart Phone',
                'verbose_name_plural': 'Smart Phones',
            },
            bases=('myshop.product',),
        ),
        migrations.AddField(
            model_name='smartphone',
            name='product',
            field=models.ForeignKey(verbose_name='Internal Storage', to='myshop.SmartPhoneModel'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='producttranslation',
            name='master',
            field=models.ForeignKey(related_name='translations', to='myshop.Product', null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='producttranslation',
            unique_together=set([('language_code', 'master')]),
        ),
        migrations.AddField(
            model_name='productimage',
            name='product',
            field=models.ForeignKey(to='myshop.Product'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='product',
            name='images',
            field=models.ManyToManyField(to='filer.Image', null=True, through='myshop.ProductImage'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='product',
            name='placeholder',
            field=cms.models.fields.PlaceholderField(slotname='Product Detail', editable=False, to='cms.Placeholder', null=True, verbose_name='Additional description for this product.'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='product',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_myshop.product_set+', editable=False, to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cartitem',
            name='product',
            field=models.ForeignKey(to='myshop.Product'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cart',
            name='customer',
            field=models.OneToOneField(related_name='cart', verbose_name='Customer', to='myshop.Customer'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cart',
            name='shipping_address',
            field=models.ForeignKey(related_name='+', default=None, to='myshop.Address', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='address',
            name='customer',
            field=models.ForeignKey(to='myshop.Customer'),
            preserve_default=True,
        ),
    ]
