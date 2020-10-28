from django.db.models import Sum
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django_fsm import transition
from shop.models.delivery import DeliveryModel, DeliveryItemModel


class SimpleShippingWorkflowMixin:
    """
    Workflow for simply marking the state of an Order while picking, packing and shipping items.
    It does not create a Delivery object.

    Add this class to ``settings.SHOP_ORDER_WORKFLOWS`` to mix it into the merchants Order model.
    It is mutual exclusive with :class:`shop.shipping.workflows.CommissionGoodsWorkflowMixin` or
    :class:`shop.shipping.workflows.PartialDeliveryWorkflowMixin`.

    It adds all the methods required for state transitions, while picking and packing
    the ordered goods for shipping.
    """
    TRANSITION_TARGETS = {
        'pick_goods': _("Picking goods"),
        'pack_goods': _("Packing goods"),
        'ship_goods': _("Prepare for shipping"),
        'ready_for_delivery': _("Ready for delivery"),
    }

    @property
    def associate_with_delivery(self):
        """
        :returns: ``True`` if this Order requires a delivery object.
        """
        return False

    @property
    def allow_partial_delivery(self):
        """
        :returns: ``True`` if partial item delivery is allowed.
        """
        return False

    @transition(field='status', source='payment_confirmed', target='pick_goods',
                custom=dict(admin=True, button_name=_("Pick the goods")))
    def pick_goods(self, by=None):
        """Change status to 'pick_goods'."""

    @transition(field='status', source='pick_goods', target='pack_goods',
                custom=dict(admin=True, button_name=_("Pack the goods")))
    def pack_goods(self, by=None):
        """Change status to 'pack_goods'."""

    @transition(field='status', source='pack_goods', target='ship_goods',
                custom=dict(admin=True, button_name=_("Prepare for shipping")))
    def ship_goods(self, by=None):
        """
        Ship the goods. This method implicitly invokes
        :method:`shop.shipping.modifiers.ShippingModifier.ship_the_goods(delivery)`
        """

    @transition(field='status', source='ship_goods', target='ready_for_delivery',
                custom=dict(auto=True))
    def prepare_for_delivery(self, by=None):
        """
        Put the parcel into the outgoing delivery.
        This method is invoked automatically by `ship_goods`.
        """

    def update_or_create_delivery(self, orderitem_data):
        """
        Hook to create a delivery object with items.
        """


class CommissionGoodsWorkflowMixin(SimpleShippingWorkflowMixin):
    """
    Workflow to commission all ordered items in one common Delivery.

    Add this class to ``settings.SHOP_ORDER_WORKFLOWS`` to mix it into the merchants Order model.
    It is mutual exclusive with :class:`shop.shipping.workflows.SimpleShippingWorkflowMixin` or
    :class:`shop.shipping.workflows.PartialDeliveryWorkflowMixin`.

    It adds all the methods required for state transitions, while picking and packing
    the ordered goods for shipping.
    """
    @property
    def associate_with_delivery(self):
        return True

    @transition(field='status', source='ship_goods', target='ready_for_delivery',
                custom=dict(auto=True))
    def prepare_for_delivery(self, by=None):
        """Put the parcel into the outgoing delivery."""

    def update_or_create_delivery(self, orderitem_data):
        """
        Update or create a Delivery object for all items of this Order object.
        """
        delivery, _ = DeliveryModel.objects.get_or_create(
            order=self,
            shipping_id__isnull=True,
            shipped_at__isnull=True,
            shipping_method=self.extra.get('shipping_modifier'),
            defaults={'fulfilled_at': timezone.now()}
        )
        for item in self.items.all():
            DeliveryItemModel.objects.create(
                delivery=delivery,
                item=item,
                quantity=item.quantity,
            )


class PartialDeliveryWorkflowMixin(CommissionGoodsWorkflowMixin):
    """
    Workflow to optionally commission ordered items partially.

    Add this class to ``settings.SHOP_ORDER_WORKFLOWS`` to mix it into the merchants Order model.
    It is mutual exclusive with :class:`shop.shipping.workflows.SimpleShippingWorkflowMixin` or
    :class:`shop.shipping.workflows.CommissionGoodsWorkflowMixin`.

    This mixin supports partial delivery, hence check that a materialized representation of the
    models :class:`shop.models.delivery.DeliveryModel` and :class:`shop.models.delivery.DeliveryItemModel`
    exists and is instantiated.

    Importing the classes :class:`shop.models.defaults.delivery.DeliveryModel` and
    :class:`shop.models.defaults.delivery_item.DeliveryItemModel` into the merchants
    ``models.py``, usually is enough. This adds all the methods required for state transitions,
    while picking, packing and shipping the ordered goods for delivery.
    """
    @property
    def allow_partial_delivery(self):
        return True

    @cached_property
    def unfulfilled_items(self):
        unfulfilled_items = 0
        for order_item in self.items.all():
            if not order_item.canceled:
                aggr = order_item.deliver_item.aggregate(delivered=Sum('quantity'))
                unfulfilled_items += order_item.quantity - (aggr['delivered'] or 0)
        return unfulfilled_items

    def ready_for_picking(self):
        return self.is_fully_paid() and self.unfulfilled_items > 0

    def ready_for_shipping(self):
        return self.delivery_set.filter(shipped_at__isnull=True).exists()

    @transition(field='status', source='*', target='pick_goods', conditions=[ready_for_picking],
                custom=dict(admin=True, button_name=_("Pick the goods")))
    def pick_goods(self, by=None):
        """Change status to 'pick_goods'."""

    @transition(field='status', source=['pick_goods'], target='pack_goods',
                custom=dict(admin=True, button_name=_("Pack the goods")))
    def pack_goods(self, by=None):
        """Prepare shipping object and change status to 'pack_goods'."""

    @transition(field='status', source='*', target='ship_goods', conditions=[ready_for_shipping],
                custom=dict(admin=True, button_name=_("Ship the goods")))
    def ship_goods(self, by=None):
        """Ship the goods."""

    @transition(field='status', source='ship_goods', target='ready_for_delivery',
                custom=dict(auto=True))
    def prepare_for_delivery(self, by=None):
        """Put the parcel into the outgoing delivery."""

    def update_or_create_delivery(self, orderitem_data):
        """
        Update or create a Delivery object and associate with selected ordered items.
        """
        delivery, _ = DeliveryModel.objects.get_or_create(
            order=self,
            shipping_id__isnull=True,
            shipped_at__isnull=True,
            shipping_method=self.extra.get('shipping_modifier'),
            defaults={'fulfilled_at': timezone.now()}
        )

        # create a DeliveryItem object for each ordered item to be shipped with this delivery
        for data in orderitem_data:
            if data['deliver_quantity'] > 0 and not data['canceled']:
                DeliveryItemModel.objects.create(
                    delivery=delivery,
                    item=data['id'],
                    quantity=data['deliver_quantity'],
                )
        if not delivery.items.exists():
            # since no OrderItem was added to this delivery, discard it
            delivery.delete()
