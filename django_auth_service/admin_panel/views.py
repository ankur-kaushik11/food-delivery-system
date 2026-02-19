"""
Views for admin panel.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Restaurant, Offer, Fee
from users.models import User
from .serializers import RestaurantSerializer, OfferSerializer, FeeSerializer, UserListSerializer


class IsAdmin(IsAuthenticated):
    """Permission class to check if user is Admin."""
    
    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        if not is_authenticated:
            return False
        return request.user.role == 'Admin'


class RestaurantViewSet(viewsets.ModelViewSet):
    """ViewSet for managing restaurants (Admin only)."""
    
    queryset = Restaurant.objects.all().select_related('owner')
    serializer_class = RestaurantSerializer
    permission_classes = [IsAdmin]
    
    def list(self, request, *args, **kwargs):
        """List all restaurants."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class OfferViewSet(viewsets.ModelViewSet):
    """ViewSet for managing offers (Admin only)."""
    
    queryset = Offer.objects.all().select_related('restaurant')
    serializer_class = OfferSerializer
    permission_classes = [IsAdmin]
    
    def list(self, request, *args, **kwargs):
        """List all offers."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class FeeViewSet(viewsets.ModelViewSet):
    """ViewSet for managing fees (Admin only)."""
    
    queryset = Fee.objects.all().select_related('restaurant')
    serializer_class = FeeSerializer
    permission_classes = [IsAdmin]
    
    def list(self, request, *args, **kwargs):
        """List all fees."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdmin])
def list_users(request):
    """List all users (Admin only)."""
    users = User.objects.all().order_by('-created_at')
    serializer = UserListSerializer(users, many=True)
    return Response(serializer.data)
