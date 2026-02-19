"""
Admin configuration for admin_panel app.
"""
from django.contrib import admin
from .models import Restaurant, Offer, Fee


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'pin_code', 'status', 'is_ordering_enabled', 'created_at']
    list_filter = ['status', 'is_ordering_enabled', 'created_at']
    search_fields = ['name', 'pin_code', 'owner__email']


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['id', 'restaurant', 'discount_percentage', 'min_order_value', 'first_time_user_only', 'active', 'created_at']
    list_filter = ['active', 'first_time_user_only', 'created_at']
    search_fields = ['restaurant__name']


@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = ['id', 'restaurant', 'delivery_fee', 'platform_fee', 'created_at']
    list_filter = ['created_at']
    search_fields = ['restaurant__name']
