from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models.base import ModelBase
from django.test import TestCase
from polymorphic.models import PolymorphicModel, PolymorphicModelBase
from shop import deferred

import copy
from types import new_class


def create_regular_class(name, fields={}, meta={}):
    meta.setdefault('app_label', 'foo')
    Meta = type(str('Meta'), (), meta)
    return type(str(name), (models.Model,), dict(Meta=Meta, __module__=__name__, **fields))


def create_deferred_base_class(name, fields={}, meta={}, polymorphic=False):
    metaclass = deferred.ForeignKeyBuilder
    model_class = models.Model

    if polymorphic:
        metaclass = deferred.PolymorphicForeignKeyBuilder
        model_class = PolymorphicModel

    meta.setdefault('app_label', 'foo')
    meta.setdefault('abstract', True)
    Meta = type(str('Meta'), (), meta)
    cls_dict = dict(Meta=Meta, __metaclass__=metaclass, __module__=__name__, **fields)
    return new_class(name, (model_class,), {'metaclass': metaclass}, lambda attrs: attrs.update(cls_dict))


def create_deferred_class(name, base, fields={}, meta={}, mixins=()):
    meta.setdefault('app_label', 'bar')
    Meta = type(str('Meta'), (), meta)
    return type(str(name), mixins + (base,), dict(Meta=Meta, __module__=__name__, **fields))


RegularUser = create_regular_class('RegularUser')
DeferredBaseUser = create_deferred_base_class('DeferredBaseUser')
DeferredUser = create_deferred_class('DeferredUser', DeferredBaseUser)


RegularCustomer = create_regular_class('RegularCustomer', {
    'user': models.OneToOneField(RegularUser, on_delete=models.PROTECT),
    'advertised_by': models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL),
})
DeferredBaseCustomer = create_deferred_base_class('DeferredBaseCustomer', {
    'user': deferred.OneToOneField(DeferredBaseUser, on_delete=models.PROTECT),
    'advertised_by': deferred.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL),
})
DeferredCustomer = create_deferred_class('DeferredCustomer', DeferredBaseCustomer)


RegularProduct = create_regular_class('RegularProduct')
DeferredBaseProduct = create_deferred_base_class('DeferredBaseProduct')
DeferredProduct = create_deferred_class('DeferredProduct', DeferredBaseProduct)


# Order is important, it must be declared before DeferredOrder, so that fulfillment tests make sense
DeferredBaseOrderItemBeforeOrder = create_deferred_base_class('DeferredBaseOrderItemBeforeOrder', {
    'order': deferred.ForeignKey('DeferredBaseOrder', on_delete=models.CASCADE),
    'product': deferred.ForeignKey(DeferredBaseProduct, on_delete=models.PROTECT),
})
DeferredOrderItemBeforeOrder = create_deferred_class('DeferredOrderItemBeforeOrder', DeferredBaseOrderItemBeforeOrder)


RegularOrder = create_regular_class('RegularOrder', {
    'customer': models.ForeignKey(RegularCustomer, on_delete=models.PROTECT),
    'items_simple': models.ManyToManyField(RegularProduct),
    'items_through_fulfill_by_order_item': models.ManyToManyField('RegularProductAfterOrder', through='RegularOrderItemAfterOrderAndProduct'),
})
DeferredBaseOrder = create_deferred_base_class('DeferredBaseOrder', {
    'customer': deferred.ForeignKey(DeferredBaseCustomer, on_delete=models.PROTECT),
    'items_simple': deferred.ManyToManyField(DeferredBaseProduct),
    'items_simple_fulfill_by_product': deferred.ManyToManyField('DeferredBaseProductAfterOrder'),
    'items_through_fulfill_by_order_item': deferred.ManyToManyField('DeferredBaseProductAfterOrder', through='DeferredBaseOrderItemAfterOrderAndProduct'),
    'items_through_fulfill_by_order': deferred.ManyToManyField(DeferredBaseProduct, through=DeferredBaseOrderItemBeforeOrder),
    'items_through_fulfill_by_product': deferred.ManyToManyField('DeferredBaseProductAfterOrder', through='DeferredBaseOrderItemBeforeProduct'),
})
DeferredOrder = create_deferred_class('DeferredOrder', DeferredBaseOrder)


# Order is important, it must be declared before DeferredProductAfterOrder, so that fulfillment tests make sense
DeferredBaseOrderItemBeforeProduct = create_deferred_base_class('DeferredBaseOrderItemBeforeProduct', {
    'order': deferred.ForeignKey(DeferredBaseOrder, on_delete=models.CASCADE),
    'product': deferred.ForeignKey('DeferredBaseProductAfterOrder', on_delete=models.PROTECT),
})
DeferredOrderItemBeforeProduct = create_deferred_class('DeferredOrderItemBeforeProduct', DeferredBaseOrderItemBeforeProduct)


# Order is important, it must be declared after DeferredOrder, so that fulfillment tests make sense
RegularProductAfterOrder = create_regular_class('RegularProductAfterOrder')
DeferredBaseProductAfterOrder = create_deferred_base_class('DeferredBaseProductAfterOrder')
DeferredProductAfterOrder = create_deferred_class('DeferredProductAfterOrder', DeferredBaseProductAfterOrder)


# Order is important, it must be declared after DeferredOrder and DeferredPrdoductAfterOrder, so that fulfillment tests make sense
RegularOrderItemAfterOrderAndProduct = create_regular_class('RegularOrderItemAfterOrderAndProduct', {
    'order': models.ForeignKey(RegularOrder, on_delete=models.CASCADE),
    'product': models.ForeignKey(RegularProductAfterOrder, on_delete=models.PROTECT),
})
DeferredBaseOrderItemAfterOrderAndProduct = create_deferred_base_class('DeferredBaseOrderItemAfterOrderAndProduct', {
    'order': deferred.ForeignKey(DeferredBaseOrder, on_delete=models.CASCADE),
    'product': deferred.ForeignKey(DeferredBaseProductAfterOrder, on_delete=models.PROTECT),
})
DeferredOrderItemAfterOrderAndProduct = create_deferred_class('DeferredOrderItemAfterOrderAndProduct', DeferredBaseOrderItemAfterOrderAndProduct)


OrderPayment = create_deferred_base_class('OrderPayment', {
    'order': deferred.ForeignKey(DeferredBaseOrder, on_delete=models.CASCADE),
}, {'abstract': False})


DeferredBaseOrderPaymentLog = create_deferred_base_class('DeferredBaseOrderPaymentLog', {
    'order_payment': deferred.ForeignKey(OrderPayment, on_delete=models.CASCADE),
})
DeferredOrderPaymentLog = create_deferred_class('DeferredOrderPaymentLog', DeferredBaseOrderPaymentLog)


DeferredBasePolymorphicProduct = create_deferred_base_class('DeferredBasePolymorphicProduct', {
    'owner': deferred.ForeignKey(DeferredBaseCustomer, on_delete=models.PROTECT),
}, polymorphic=True)
DeferredPolymorphicProduct = create_deferred_class('DeferredPolymorphicProduct', DeferredBasePolymorphicProduct)


class DeferredTestCase(TestCase):

    def assert_same_model(self, to, model):
        if isinstance(to, str):
            self.assertEqual(to, model.__name__)
        else:
            self.assertIs(to, model)

    def _test_foreign_key(self, from_class, to_class, field_attribute):
        field = from_class._meta.get_field(field_attribute)

        self.assertTrue(field.is_relation)
        self.assertTrue(field.many_to_one)
        self.assert_same_model(field.related_model, to_class)

    def test_foreign_key_regular(self):
        self._test_foreign_key(RegularOrder, RegularCustomer, 'customer')

    def test_foreign_key_deferred(self):
        self._test_foreign_key(DeferredOrder, DeferredCustomer, 'customer')

    def _test_one_to_one_field(self, customer_class, user_class):
        user_field = customer_class._meta.get_field('user')

        self.assertTrue(user_field.is_relation)
        self.assertTrue(user_field.one_to_one)
        self.assert_same_model(user_field.related_model, user_class)

    def test_one_to_one_field_regular(self):
        self._test_one_to_one_field(RegularCustomer, RegularUser)

    def test_one_to_one_field_deferred(self):
        self._test_one_to_one_field(DeferredCustomer, DeferredUser)

    def _test_many_to_may_field_simple(self, order_class, product_class, items_field_attribute):
        items_field = order_class._meta.get_field(items_field_attribute)

        self.assertTrue(items_field.is_relation)
        self.assertTrue(items_field.many_to_many)
        self.assert_same_model(items_field.related_model, product_class)

        m2m_field_name = items_field.m2m_field_name()
        m2m_field = items_field.remote_field.through._meta.get_field(m2m_field_name)
        m2m_reverse_field_name = items_field.m2m_reverse_field_name()
        m2m_reverse_field = items_field.remote_field.through._meta.get_field(m2m_reverse_field_name)

        self.assert_same_model(m2m_field.related_model, order_class)
        self.assert_same_model(m2m_reverse_field.related_model, product_class)

    def test_many_to_many_field_simple_regular(self):
        self._test_many_to_may_field_simple(
            RegularOrder,
            RegularProduct,
            items_field_attribute='items_simple',
        )

    def test_many_to_many_field_simple_deferred(self):
        self._test_many_to_may_field_simple(
            DeferredOrder,
            DeferredProduct,
            items_field_attribute='items_simple',
        )

    def test_many_to_many_field_simple_deferred_by_product(self):
        self._test_many_to_may_field_simple(
            DeferredOrder,
            DeferredProductAfterOrder,
            items_field_attribute='items_simple_fulfill_by_product',
        )

    def _test_many_to_may_field_through(self, order_class, product_class, order_item_class, items_field_attribute):
        items_field = order_class._meta.get_field(items_field_attribute)

        self.assertTrue(items_field.is_relation)
        self.assertTrue(items_field.many_to_many)
        self.assert_same_model(items_field.related_model, product_class)
        self.assert_same_model(items_field.remote_field.through, order_item_class)

        m2m_field_name = items_field.m2m_field_name()
        m2m_field = items_field.remote_field.through._meta.get_field(m2m_field_name)
        m2m_reverse_field_name = items_field.m2m_reverse_field_name()
        m2m_reverse_field = items_field.remote_field.through._meta.get_field(m2m_reverse_field_name)

        self.assert_same_model(m2m_field.related_model, order_class)
        self.assert_same_model(m2m_reverse_field.related_model, product_class)

    def test_many_to_many_field_through_regular(self):
        self._test_many_to_may_field_through(
            RegularOrder,
            RegularProductAfterOrder,
            RegularOrderItemAfterOrderAndProduct,
            items_field_attribute='items_through_fulfill_by_order_item',
        )

    def test_many_to_many_field_through_deferred(self):
        self._test_many_to_may_field_through(
            DeferredOrder,
            DeferredProductAfterOrder,
            DeferredOrderItemAfterOrderAndProduct,
            items_field_attribute='items_through_fulfill_by_order_item',
        )

    def test_many_to_many_field_through_deferred_by_order(self):
        self._test_many_to_may_field_through(
            DeferredOrder,
            DeferredProduct,
            DeferredOrderItemBeforeOrder,
            items_field_attribute='items_through_fulfill_by_order',
        )

    def test_many_to_many_field_through_deferred_by_product(self):
        self._test_many_to_may_field_through(
            DeferredOrder,
            DeferredProductAfterOrder,
            DeferredOrderItemBeforeProduct,
            items_field_attribute='items_through_fulfill_by_product',
        )

    def _test_foreign_key_self(self, customer_class):
        advertised_by_field = customer_class._meta.get_field('advertised_by')

        self.assertTrue(advertised_by_field.is_relation)
        self.assertTrue(advertised_by_field.many_to_one)
        self.assert_same_model(advertised_by_field.related_model, customer_class)

    def test_foreign_key_self_regular(self):
        self._test_foreign_key_self(RegularCustomer)

    def test_foreign_key_self_deferred(self):
        self._test_foreign_key_self(DeferredCustomer)

    def test_extend_deferred_model_allowed(self):
        """
        Extending a deferred model is allowed,
        but deferred relations will still reference the (first) deferred model.
        """
        create_deferred_class('Customer', DeferredCustomer)

        OrderBase = create_deferred_base_class('OrderBase', {
            'customer': deferred.ForeignKey(DeferredBaseCustomer, on_delete=models.PROTECT),
        })
        Order = create_deferred_class('Order', OrderBase)

        self._test_foreign_key(DeferredOrder, DeferredCustomer, 'customer')
        self._test_foreign_key(Order, DeferredCustomer, 'customer')

    def test_extend_deferred_base_model_allowed_only_once(self):
        with self.assertRaisesRegex(ImproperlyConfigured, "Both Model classes 'Product' and 'DeferredProduct' inherited from abstract base class DeferredBaseProduct"):
            create_deferred_class('Product', DeferredBaseProduct)

    def test_non_abstract_deferred_base_model_allowed(self):
        self._test_foreign_key(OrderPayment, DeferredOrder, 'order')
        self._test_foreign_key(DeferredOrderPaymentLog, OrderPayment, 'order_payment'),

    def test_extend_non_abstract_deferred_base_model_allowed(self):
        """
        Extending a non abstract deferred model is allowed,
        but deferred relations will still reference the (first) deferred model.
        """
        create_deferred_class('OrderPaymentSubclass', OrderPayment)

        BaseOrderPaymentLog = create_deferred_base_class('BaseOrderPaymentLog', {
            'order_payment': deferred.ForeignKey(OrderPayment, on_delete=models.CASCADE),
        })
        OrderPaymentLog = create_deferred_class('OrderPaymentLog', BaseOrderPaymentLog)

        self._test_foreign_key(DeferredOrderPaymentLog, OrderPayment, 'order_payment')
        self._test_foreign_key(OrderPaymentLog, OrderPayment, 'order_payment')

    def test_extend_non_abstract_deferred_base_model_always_allowed(self):
        create_deferred_class('OrderPaymentSubclass1', OrderPayment)
        create_deferred_class('OrderPaymentSubclass2', OrderPayment)

    def test_polymorphic_base_model(self):
        self.assertTrue(issubclass(DeferredPolymorphicProduct, PolymorphicModel))
        self.assertTrue(isinstance(DeferredPolymorphicProduct, PolymorphicModelBase))
        self._test_foreign_key(DeferredPolymorphicProduct, DeferredCustomer, 'owner')

    def test_mixins_allowed(self):
        SomeMixin = type(str('SomeMixin'), (object,), {})
        BaseModel = create_regular_class('BaseModel', meta={'abstract': True})
        MixinBaseProduct = create_deferred_base_class('MixinBaseProduct')
        MixinProduct = create_deferred_class('MixinProduct', MixinBaseProduct, mixins=(SomeMixin, BaseModel))

        self.assertTrue(issubclass(MixinProduct, SomeMixin))
        self.assertTrue(issubclass(MixinProduct, BaseModel))

    def test_check_for_pending_mappings(self):
        deferred.ForeignKeyBuilder.check_for_pending_mappings()

        PendingMappingBaseCustomer = create_deferred_base_class('PendingMappingBaseCustomer')
        PendingMappingBaseOrder = create_deferred_base_class('PendingMappingBaseOrder', {
            'customer': deferred.ForeignKey(PendingMappingBaseCustomer, on_delete=models.PROTECT),
        })

        deferred.ForeignKeyBuilder.check_for_pending_mappings()

        create_deferred_class('PendingMappingOrder', PendingMappingBaseOrder)

        with self.assertRaisesRegex(ImproperlyConfigured, "Deferred foreign key 'PendingMappingOrder.customer' has not been mapped"):
            deferred.ForeignKeyBuilder.check_for_pending_mappings()


class MaterializedModelTestCase(TestCase):

    def setUp(self):
        self.OrderModel = deferred.MaterializedModel(DeferredBaseOrder)

    def test_types(self):
        self.assertTrue(isinstance(self.OrderModel, ModelBase))
        self.assertTrue(issubclass(self.OrderModel, models.Model))
        self.assertIs(type(self.OrderModel), deferred.MaterializedModel)

    def test_call(self):
        order = self.OrderModel()

        self.assertTrue(isinstance(order, DeferredOrder))

    def test_repr(self):
        self.assertEqual(repr(self.OrderModel), "<MaterializedModel: <class 'test_deferred.DeferredBaseOrder'>>")

        self.OrderModel._setup()

        self.assertEqual(repr(self.OrderModel), "<MaterializedModel: <class 'test_deferred.DeferredOrder'>>")

    def test_copy_uninitialized(self):
        OrderModelDeepCopy = copy.copy(self.OrderModel)

        self.assertIs(type(OrderModelDeepCopy), deferred.MaterializedModel)

        # Ensure that base_model was copied
        OrderModelDeepCopy._setup()

    def test_copy_initialized(self):
        self.OrderModel._setup()
        OrderModelDeepCopy = copy.copy(self.OrderModel)

        self.assertIs(OrderModelDeepCopy, DeferredOrder)

    def test_deepcopy_uninitialized(self):
        OrderModelDeepCopy = copy.deepcopy(self.OrderModel)

        self.assertIs(type(OrderModelDeepCopy), deferred.MaterializedModel)

        # Ensure that base_model was copied
        OrderModelDeepCopy._setup()

    def test_deepcopy_initialized(self):
        self.OrderModel._setup()
        OrderModelDeepCopy = copy.deepcopy(self.OrderModel)

        self.assertIs(OrderModelDeepCopy, DeferredOrder)

    def test_error_when_initializing_unmapped_model(self):
        Unmapped = create_deferred_base_class('Unmapped')
        UnmappedModel = deferred.MaterializedModel(Unmapped)

        with self.assertRaisesRegex(ImproperlyConfigured, 'No class implements abstract base model: `Unmapped`.'):
            UnmappedModel._setup()
