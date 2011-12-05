# flake8: noqa
# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'Product'
        db.create_table('shop_product', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('polymorphic_ctype', self.gf('django.db.models.fields.related.ForeignKey')(related_name='polymorphic_shop.product_set', null=True, to=orm['contenttypes.ContentType'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('short_description', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('long_description', self.gf('django.db.models.fields.TextField')()),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('unit_price', self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=12, decimal_places=2)),
        ))
        db.send_create_signal('shop', ['Product'])

        # Adding model 'Cart'
        db.create_table('shop_cart', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('shop', ['Cart'])

        # Adding model 'CartItem'
        db.create_table('shop_cartitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cart', self.gf('django.db.models.fields.related.ForeignKey')(related_name='items', to=orm['shop.Cart'])),
            ('quantity', self.gf('django.db.models.fields.IntegerField')()),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.Product'])),
        ))
        db.send_create_signal('shop', ['CartItem'])

        # Adding model 'Client'
        db.create_table('shop_client', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(related_name='client', unique=True, to=orm['auth.User'])),
            ('date_of_birth', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('shop', ['Client'])

        # Adding model 'Country'
        db.create_table('shop_country', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('shop', ['Country'])

        # Adding model 'Address'
        db.create_table('shop_address', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('client', self.gf('django.db.models.fields.related.ForeignKey')(related_name='addresses', to=orm['shop.Client'])),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('address2', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.Country'])),
            ('is_shipping', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_billing', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('shop', ['Address'])

        # Adding model 'Order'
        db.create_table('shop_order', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('order_subtotal', self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=12, decimal_places=2)),
            ('order_total', self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=12, decimal_places=2)),
            ('payment_method', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('shipping_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('shipping_address', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('shipping_address2', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('shipping_city', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('shipping_zip_code', self.gf('django.db.models.fields.CharField')(max_length=20, null=True)),
            ('shipping_state', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('shipping_country', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('billing_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('billing_address', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('billing_address2', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('billing_city', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('billing_zip_code', self.gf('django.db.models.fields.CharField')(max_length=20, null=True)),
            ('billing_state', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('billing_country', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('shop', ['Order'])

        # Adding model 'OrderItem'
        db.create_table('shop_orderitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(related_name='items', to=orm['shop.Order'])),
            ('product_reference', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('product_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('unit_price', self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=12, decimal_places=2)),
            ('quantity', self.gf('django.db.models.fields.IntegerField')()),
            ('line_subtotal', self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=12, decimal_places=2)),
            ('line_total', self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=12, decimal_places=2)),
        ))
        db.send_create_signal('shop', ['OrderItem'])

        # Adding model 'OrderExtraInfo'
        db.create_table('shop_orderextrainfo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(related_name='extra_info', to=orm['shop.Order'])),
            ('text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('shop', ['OrderExtraInfo'])

        # Adding model 'ExtraOrderPriceField'
        db.create_table('shop_extraorderpricefield', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.Order'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=12, decimal_places=2)),
            ('is_shipping', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('shop', ['ExtraOrderPriceField'])

        # Adding model 'ExtraOrderItemPriceField'
        db.create_table('shop_extraorderitempricefield', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order_item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.OrderItem'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=12, decimal_places=2)),
        ))
        db.send_create_signal('shop', ['ExtraOrderItemPriceField'])

        # Adding model 'OrderPayment'
        db.create_table('shop_orderpayment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.Order'])),
            ('amount', self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=12, decimal_places=2)),
            ('transaction_id', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('payment_method', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('shop', ['OrderPayment'])


    def backwards(self, orm):

        # Deleting model 'Product'
        db.delete_table('shop_product')

        # Deleting model 'Cart'
        db.delete_table('shop_cart')

        # Deleting model 'CartItem'
        db.delete_table('shop_cartitem')

        # Deleting model 'Client'
        db.delete_table('shop_client')

        # Deleting model 'Country'
        db.delete_table('shop_country')

        # Deleting model 'Address'
        db.delete_table('shop_address')

        # Deleting model 'Order'
        db.delete_table('shop_order')

        # Deleting model 'OrderItem'
        db.delete_table('shop_orderitem')

        # Deleting model 'OrderExtraInfo'
        db.delete_table('shop_orderextrainfo')

        # Deleting model 'ExtraOrderPriceField'
        db.delete_table('shop_extraorderpricefield')

        # Deleting model 'ExtraOrderItemPriceField'
        db.delete_table('shop_extraorderitempricefield')

        # Deleting model 'OrderPayment'
        db.delete_table('shop_orderpayment')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'shop.address': {
            'Meta': {'object_name': 'Address'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'address2': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'client': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'addresses'", 'to': "orm['shop.Client']"}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Country']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_billing': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_shipping': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'shop.cart': {
            'Meta': {'object_name': 'Cart'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'shop.cartitem': {
            'Meta': {'object_name': 'CartItem'},
            'cart': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'to': "orm['shop.Cart']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Product']"}),
            'quantity': ('django.db.models.fields.IntegerField', [], {})
        },
        'shop.client': {
            'Meta': {'object_name': 'Client'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_of_birth': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'client'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'shop.country': {
            'Meta': {'object_name': 'Country'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'shop.extraorderitempricefield': {
            'Meta': {'object_name': 'ExtraOrderItemPriceField'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order_item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.OrderItem']"}),
            'value': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '12', 'decimal_places': '2'})
        },
        'shop.extraorderpricefield': {
            'Meta': {'object_name': 'ExtraOrderPriceField'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_shipping': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Order']"}),
            'value': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '12', 'decimal_places': '2'})
        },
        'shop.order': {
            'Meta': {'object_name': 'Order'},
            'billing_address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'billing_address2': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'billing_city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'billing_country': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'billing_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'billing_state': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'billing_zip_code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'order_subtotal': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '12', 'decimal_places': '2'}),
            'order_total': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '12', 'decimal_places': '2'}),
            'payment_method': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'shipping_address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'shipping_address2': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'shipping_city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'shipping_country': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'shipping_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'shipping_state': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'shipping_zip_code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'shop.orderextrainfo': {
            'Meta': {'object_name': 'OrderExtraInfo'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'extra_info'", 'to': "orm['shop.Order']"}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        'shop.orderitem': {
            'Meta': {'object_name': 'OrderItem'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_subtotal': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '12', 'decimal_places': '2'}),
            'line_total': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '12', 'decimal_places': '2'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'to': "orm['shop.Order']"}),
            'product_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'product_reference': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {}),
            'unit_price': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '12', 'decimal_places': '2'})
        },
        'shop.orderpayment': {
            'Meta': {'object_name': 'OrderPayment'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '12', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shop.Order']"}),
            'payment_method': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'transaction_id': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'shop.product': {
            'Meta': {'object_name': 'Product'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'long_description': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'polymorphic_shop.product_set'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'short_description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'unit_price': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '12', 'decimal_places': '2'})
        }
    }

    complete_apps = ['shop']
