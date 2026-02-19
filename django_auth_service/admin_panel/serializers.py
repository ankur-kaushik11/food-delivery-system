"""
Serializers for admin panel.
"""
from rest_framework import serializers
from .models import Restaurant, Offer, Fee
from users.models import User


class RestaurantSerializer(serializers.ModelSerializer):
    """Serializer for Restaurant model."""
    
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    owner_name = serializers.CharField(source='owner.name', read_only=True)
    
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'owner', 'owner_email', 'owner_name', 'pin_code', 'status', 'is_ordering_enabled', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_owner(self, value):
        """Validate that owner has Restaurant Owner role."""
        if value.role != 'Restaurant Owner':
            raise serializers.ValidationError("Owner must have 'Restaurant Owner' role.")
        return value


class OfferSerializer(serializers.ModelSerializer):
    """Serializer for Offer model."""
    
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True, allow_null=True)
    
    class Meta:
        model = Offer
        fields = ['id', 'restaurant', 'restaurant_name', 'discount_percentage', 'min_order_value', 'first_time_user_only', 'active', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_discount_percentage(self, value):
        """Validate discount percentage is between 0 and 100."""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Discount percentage must be between 0 and 100.")
        return value


class FeeSerializer(serializers.ModelSerializer):
    """Serializer for Fee model."""
    
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True, allow_null=True)
    
    class Meta:
        model = Fee
        fields = ['id', 'restaurant', 'restaurant_name', 'delivery_fee', 'platform_fee', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate(self, attrs):
        """Validate fees are non-negative."""
        if attrs.get('delivery_fee', 0) < 0:
            raise serializers.ValidationError({"delivery_fee": "Delivery fee cannot be negative."})
        if attrs.get('platform_fee', 0) < 0:
            raise serializers.ValidationError({"platform_fee": "Platform fee cannot be negative."})
        return attrs


class UserListSerializer(serializers.ModelSerializer):
    """Serializer for listing users."""
    
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'role', 'pin_code', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
