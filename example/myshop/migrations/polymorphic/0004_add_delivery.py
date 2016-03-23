# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myshop', '0003_add_polymorphic'),
    ]

    operations = [
        migrations.CreateModel(
            name='Delivery',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('shipping_id', models.CharField(help_text="The transaction processor's reference", max_length=255, null=True, verbose_name='Shipping ID', blank=True)),
                ('fulfilled_at', models.DateTimeField(null=True, verbose_name='Fulfilled at', blank=True)),
                ('shipped_at', models.DateTimeField(null=True, verbose_name='Shipped at', blank=True)),
                ('shipping_method', models.CharField(help_text='The shipping backend used to deliver the items for this order', max_length=50, verbose_name='Shipping method')),
                ('order', models.ForeignKey(to='myshop.Order')),
            ],
        ),
        migrations.CreateModel(
            name='DeliveryItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.IntegerField(default=0, verbose_name='Delivered quantity')),
                ('delivery', models.ForeignKey(verbose_name='Delivery', to='myshop.Delivery', help_text='Refer to the shipping provider used to ship this item')),
            ],
        ),
        migrations.RemoveField(
            model_name='orderpayment',
            name='status',
        ),
        migrations.AddField(
            model_name='orderitem',
            name='canceled',
            field=models.BooleanField(default=False, verbose_name='Item canceled '),
        ),
        migrations.AlterField(
            model_name='orderpayment',
            name='payment_method',
            field=models.CharField(help_text='The payment backend used to process the purchase', max_length=50, verbose_name='Payment method'),
        ),
        migrations.AddField(
            model_name='deliveryitem',
            name='item',
            field=models.ForeignKey(verbose_name='Ordered item', to='myshop.OrderItem'),
        ),
    ]
