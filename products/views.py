from rest_framework import viewsets, permissions, status
from .models import Product, Fee
from .serializers import ProductSerializer, FeeSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

class ProductFilter(filters.FilterSet):
    min_interest_rate = filters.NumberFilter(field_name='interest_rate', lookup_expr='gte')
    max_interest_rate = filters.NumberFilter(field_name='interest_rate', lookup_expr='lte')
    loan_amount = filters.NumberFilter(method='filter_by_loan_amount')
    credit_score = filters.NumberFilter(method='filter_by_credit_score')
    
    class Meta:
        model = Product
        fields = ['is_active', 'min_interest_rate', 'max_interest_rate', 'loan_amount', 'credit_score']
    
    def filter_by_loan_amount(self, queryset, name, value):
        return queryset.filter(min_loan_amount__lte=value, max_loan_amount__gte=value)
    
    def filter_by_credit_score(self, queryset, name, value):
        return queryset.filter(min_credit_score__lte=value)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'interest_rate']

class FeeViewSet(viewsets.ModelViewSet):
    serializer_class = FeeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        return Fee.objects.filter(product_id=product_id)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        product_id = self.kwargs.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        
        # Create a mutable copy of the request data
        data = request.data.copy()
        # Add the product ID to the data
        data['product'] = product.id
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
