"""
Models for admin panel (using existing tables from FastAPI).
"""
from django.db import models
from users.models import User


class Restaurant(models.Model):
    """Restaurant model (matches FastAPI schema)."""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_restaurants')
    pin_code = models.CharField(max_length=10)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_ordering_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'restaurants'
        managed = False  # Django won't create/modify this table
    
    def __str__(self):
        return self.name


class Offer(models.Model):
    """Offer model (matches FastAPI schema)."""
    
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True, blank=True, related_name='offers')
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2)
    first_time_user_only = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'offers'
        managed = False
    
    def __str__(self):
        return f"{self.discount_percentage}% off (min: {self.min_order_value})"


class Fee(models.Model):
    """Fee model (matches FastAPI schema)."""
    
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True, blank=True, related_name='fees')
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'fees'
        managed = False
    
    def __str__(self):
        return f"Delivery: {self.delivery_fee}, Platform: {self.platform_fee}"
