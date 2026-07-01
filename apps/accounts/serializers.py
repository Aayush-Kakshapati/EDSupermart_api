from rest_framework import serializers
from .models import User
import re

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "phone", "address", "role"]

    def validate_phone(self, value):
        if not re.match(r"^\+?\d{10-15}$", value):
            raise serializers.ValidationError("Enter a valid phone number")
        return value
    