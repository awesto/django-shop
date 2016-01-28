# flake8: noqa
# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Deleting field 'Order.billing_zip_code'
        db.delete_column('shop_order', 'billing_zip_code')

        # Deleting field 'Order.shipping_address2'
        db.delete_column('shop_order', 'shipping_address2')

        # Deleting field 'Order.billing_name'
        db.delete_column('shop_order', 'billing_name')

        # Deleting field 'Order.shipping_zip_code'
        db.delete_column('shop_order', 'shipping_zip_code')

        # Deleting field 'Order.billing_country'
        db.delete_column('shop_order', 'billing_country')

        # Deleting field 'Order.shipping_name'
        db.delete_column('shop_order', 'shipping_name')

        # Deleting field 'Order.billing_address'
        db.delete_column('shop_order', 'billing_address')

        # Deleting field 'Order.shipping_city'
        db.delete_column('shop_order', 'shipping_city')

        # Deleting field 'Order.billing_address2'
        db.delete_column('shop_order', 'billing_address2')

        # Deleting field 'Order.shipping_state'
        db.delete_column('shop_order', 'shipping_state')

        # Deleting field 'Order.billing_city'
        db.delete_column('shop_order', 'billing_city')

        # Deleting field 'Order.shipping_address'
        db.delete_column('shop_order', 'shipping_address')

        # Deleting field 'Order.shipping_country'
        db.delete_column('shop_order', 'shipping_country')

        # Deleting field 'Order.billing_state'
        db.delete_column('shop_order', 'billing_state')

        # Adding field 'Order.shipping_address_text'
        db.add_column('shop_order', 'shipping_address_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)

        # Adding field 'Order.billing_address_text'
        db.add_column('shop_order', 'billing_address_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)


    def backwards(self, orm):

        # Adding field 'Order.billing_zip_code'
        db.add_column('shop_order', 'billing_zip_code', self.gf('django.db.models.fields.CharField')(max_length=20, null=True), keep_default=False)

        # Adding field 'Order.shipping_address2'
        db.add_column('shop_order', 'shipping_address2', self.gf('django.db.models.fields.CharField')(max_length=255, null=True), keep_default=False)

        # Adding field 'Order.billing_name'
        db.add_column('shop_order', 'billing_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True), keep_default=False)

        # Adding field 'Order.shipping_zip_code'
        db.add_column('shop_order', 'shipping_zip_code', self.gf('django.db.models.fields.CharField')(max_length=20, null=True), keep_default=False)

        # Adding field 'Order.billing_country'
        db.add_column('shop_order', 'billing_country', self.gf('django.db.models.fields.CharField')(max_length=255, null=True), keep_default=False)

        # Adding field 'Order.shipping_name'
        db.add_column('shop_order', 'shipping_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True), keep_default=False)

        # Adding field 'Order.billing_address'
        db.add_column('shop_order', 'billing_address', self.gf('django.db.models.fields.CharField')(max_length=255, null=True), keep_default=False)

        # Adding field 'Order.shipping_city'
        db.add_column('shop_order', 'shipping_city', self.gf('django.db.models.fields.CharField')(max_length=255, null=True), keep_default=False)

        # Adding field 'Order.billing_address2'
        db.add_column('shop_order', 'billing_address2', self.gf('django.db.models.fields.CharField')(max_length=255, null=True), keep_default=False)

        # Adding field 'Order.shipping_state'
        db.add_column('shop_order', 'shipping_state', self.gf('django.db.models.fields.CharField')(max_length=255, null=True), keep_default=False)

        # Adding field 'Order.billing_city'
        db.add_column('shop_order', 'billing_city', self.gf('django.db.models.fields.CharField')(max_length=255, null=True), keep_default=False)

        # Adding field 'Order.shipping_address'
        db.add_column('shop_order', 'shipping_address', self.gf('django.db.models.fields.CharField')(max_length=255, null=True), keep_default=False)

        # Adding field 'Order.shipping_country'
        db.add_column('shop_order', 'shipping_country', self.gf('django.db.models.fields.CharField')(max_length=255, null=True), keep_default=False)

        # Adding field 'Order.billing_state'
        db.add_column('shop_order', 'billing_state', self.gf('django.db.models.fields.CharField')(max_length=255, null=True), keep_default=False)

        # Deleting field 'Order.shipping_address_text'
        db.delete_column('shop_order', 'shipping_address_text')

        # Deleting field 'Order.billing_address_text'
        db.delete_column('shop_order', 'billing_address_text')


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
            'billing_address_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'order_subtotal': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '12', 'decimal_places': '2'}),
            'order_total': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '12', 'decimal_places': '2'}),
            'payment_method': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'shipping_address_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'polymorphic_shop.product_set'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'unit_price': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '12', 'decimal_places': '2'})
        }
    }

    complete_apps = ['shop']
