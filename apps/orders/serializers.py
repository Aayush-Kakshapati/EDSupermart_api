from django.db import transaction
from rest_framework import serializers
from .models import Order, OrderItem
from apps.products.models import Product
from apps.products.serializers import ProductSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'quantity', 'price', 'created_at']
        read_only_fields = ['created_at', 'price']


class OrderItemCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'email', 'status', 'total_amount', 'order_items', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = ['email', 'items']

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("At least one item is required.")

        for item in items:
            try:
                product = Product.objects.get(id=item['product_id'])
            except Product.DoesNotExist:
                raise serializers.ValidationError(
                    f"Product with id {item['product_id']} does not exist."
                )
            if product.stock < item['quantity']:
                raise serializers.ValidationError(
                    f"Not enough stock for {product.name}. Only {product.stock} available."
                )
        return items

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        total_amount = 0
        for item_data in items_data:
            product = Product.objects.select_for_update().get(id=item_data['product_id'])
            quantity = item_data['quantity']
            price = product.price

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=price,
            )

            product.stock -= quantity
            product.save(update_fields=['stock'])
            total_amount += price * quantity

        order.total_amount = total_amount
        order.save(update_fields=['total_amount'])

        return order
