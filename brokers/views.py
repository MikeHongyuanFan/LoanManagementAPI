from rest_framework import viewsets, permissions
from .models import Broker
from .serializers import BrokerSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

class BrokerViewSet(viewsets.ModelViewSet):
    queryset = Broker.objects.all()
    serializer_class = BrokerSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['created_at']  # Removed 'state' as it doesn't exist in the model
    search_fields = ['first_name', 'last_name', 'email', 'phone_number', 'company_name']  # Changed 'phone' to 'phone_number'
    ordering_fields = ['created_at', 'first_name', 'last_name', 'company_name']
