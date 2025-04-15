from rest_framework import viewsets, permissions, status
from .models import Borrower
from .serializers import BorrowerSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from datetime import date

class BorrowerViewSet(viewsets.ModelViewSet):
    queryset = Borrower.objects.all()
    serializer_class = BorrowerSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['state', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone_number']
    ordering_fields = ['created_at', 'first_name', 'last_name']
    
    def create(self, request, *args, **kwargs):
        """
        Override to add additional validation
        """
        # Validate date of birth is not in the future
        if 'dob' in request.data:
            try:
                dob = date.fromisoformat(request.data['dob'])
                if dob > date.today():
                    return Response(
                        {"dob": "Date of birth cannot be in the future."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                return Response(
                    {"dob": "Invalid date format. Use YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """
        Override to add additional validation
        """
        # Validate date of birth is not in the future
        if 'dob' in request.data:
            try:
                dob = date.fromisoformat(request.data['dob'])
                if dob > date.today():
                    return Response(
                        {"dob": "Date of birth cannot be in the future."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                return Response(
                    {"dob": "Invalid date format. Use YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return super().update(request, *args, **kwargs)
