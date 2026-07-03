from rest_framework import serializers
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'quantity', 'created_at']
        read_only_fields = ['created_at',]

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many= True, read_only= True)

    class Meta: 
        model = Cart
        fields = ['id','user', 'items', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']