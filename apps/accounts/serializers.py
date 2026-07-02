from rest_framework import serializers
from .models import User
import re

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "phone", "address", "role"]

    def validate_phone(self, value):
        if not re.match(r"^\+?\d{10,15}$", value):
            raise serializers.ValidationError("Enter a valid phone number")
        return value

class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ["id", "username", "email", "phone", "address", "password", "role"]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_phone(self, value):
        if not re.match(r"^\+?\d{10,15}$", value):
            raise serializers.ValidationError("Enter a valid phone number")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user
    