from rest_framework import viewsets, permissions
from .models import Broker
from .serializers import BrokerSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters

class BrokerFilter(filters.FilterSet):
    min_experience = filters.NumberFilter(field_name='years_of_experience', lookup_expr='gte')
    max_experience = filters.NumberFilter(field_name='years_of_experience', lookup_expr='lte')
    
    class Meta:
        model = Broker
        fields = ['created_at']

class BrokerViewSet(viewsets.ModelViewSet):
    queryset = Broker.objects.all()
    serializer_class = BrokerSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BrokerFilter
    search_fields = ['first_name', 'last_name', 'email', 'phone_number', 'company_name']
    ordering_fields = ['created_at', 'first_name', 'last_name', 'years_of_experience']
