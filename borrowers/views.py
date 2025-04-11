from rest_framework import viewsets, permissions
from .models import Borrower
from .serializers import BorrowerSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

class BorrowerViewSet(viewsets.ModelViewSet):
    queryset = Borrower.objects.all()
    serializer_class = BorrowerSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['state', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone_number']  # Changed 'phone' to 'phone_number'
    ordering_fields = ['created_at', 'first_name', 'last_name']
