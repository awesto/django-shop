# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers


class ProductVariantSerializer(serializers.ListSerializer):
    def update(self, instance, validated_data):
        item_mapping = {item.id: item for item in getattr(instance, self.field_name).all()}

        items, data_mapping = [], []
        for data in validated_data:
            if 'id' in data:
                # perform updates
                data_mapping.append(data['id'])
                item = item_mapping.get(data['id'])
                items.append(self.child.update(item, data))
            else:
                # perform creations
                data.update(product=self.parent.instance)
                items.append(self.child.create(data))

        # perform deletions
        for item_id, item in item_mapping.items():
            if item_id not in data_mapping:
                item.delete()

        return items
