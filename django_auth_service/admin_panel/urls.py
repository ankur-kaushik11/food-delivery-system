"""
URL configuration for admin panel.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RestaurantViewSet, OfferViewSet, FeeViewSet, list_users

router = DefaultRouter()
router.register('restaurants', RestaurantViewSet, basename='restaurant')
router.register('offers', OfferViewSet, basename='offer')
router.register('fees', FeeViewSet, basename='fee')

urlpatterns = [
    path('', include(router.urls)),
    path('users', list_users, name='list_users'),
]
