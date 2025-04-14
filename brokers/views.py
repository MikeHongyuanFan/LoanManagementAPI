from rest_framework import viewsets, permissions, status
from .models import Broker
from .serializers import BrokerSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

class BrokerFilter(filters.FilterSet):
    min_experience = filters.NumberFilter(field_name='years_of_experience', lookup_expr='gte')
    max_experience = filters.NumberFilter(field_name='years_of_experience', lookup_expr='lte')
    
    class Meta:
        model = Broker
        fields = ['created_at']
        
    def filter_queryset(self, queryset):
        """
        Override to add validation for experience filters
        """
        for name, value in self.form.cleaned_data.items():
            if name in ['min_experience', 'max_experience'] and value is not None:
                try:
                    int(value)
                except (ValueError, TypeError):
                    raise ValidationError({name: f"'{value}' is not a valid integer."})
        return super().filter_queryset(queryset)

class BrokerViewSet(viewsets.ModelViewSet):
    queryset = Broker.objects.all()
    serializer_class = BrokerSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BrokerFilter
    search_fields = ['first_name', 'last_name', 'email', 'phone_number', 'company_name']
    ordering_fields = ['created_at', 'first_name', 'last_name', 'years_of_experience']
    
    def create(self, request, *args, **kwargs):
        """
        Override to add additional validation
        """
        # Validate years_of_experience is not negative
        if 'years_of_experience' in request.data:
            try:
                years = int(request.data['years_of_experience'])
                if years < 0:
                    return Response(
                        {"years_of_experience": "Years of experience cannot be negative."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except (ValueError, TypeError):
                return Response(
                    {"years_of_experience": "Years of experience must be a valid integer."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """
        Override to add additional validation
        """
        # Validate years_of_experience is not negative
        if 'years_of_experience' in request.data:
            try:
                years = int(request.data['years_of_experience'])
                if years < 0:
                    return Response(
                        {"years_of_experience": "Years of experience cannot be negative."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except (ValueError, TypeError):
                return Response(
                    {"years_of_experience": "Years of experience must be a valid integer."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return super().update(request, *args, **kwargs)
