from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Application, Valuer, QS, Referral, Fee, Repayment, LoanExtension
from .serializers import (
    ApplicationSerializer, ApplicationDetailSerializer, ValuerSerializer, 
    QSSerializer, ReferralSerializer, FeeSerializer, RepaymentSerializer,
    LoanExtensionSerializer
)
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

class ValuerViewSet(viewsets.ModelViewSet):
    queryset = Valuer.objects.all()
    serializer_class = ValuerSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'contact_info']
    ordering_fields = ['name', 'created_at']

class QSViewSet(viewsets.ModelViewSet):
    queryset = QS.objects.all()
    serializer_class = QSSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'contact_info']
    ordering_fields = ['name', 'created_at']

class ReferralViewSet(viewsets.ModelViewSet):
    queryset = Referral.objects.all()
    serializer_class = ReferralSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'source']
    ordering_fields = ['name', 'created_at']

class FeeViewSet(viewsets.ModelViewSet):
    queryset = Fee.objects.all()
    serializer_class = FeeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'application']
    search_fields = ['name']
    ordering_fields = ['created_at', 'amount']

class RepaymentViewSet(viewsets.ModelViewSet):
    queryset = Repayment.objects.all()
    serializer_class = RepaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'application', 'due_date']
    ordering_fields = ['due_date', 'amount']

class LoanExtensionViewSet(viewsets.ModelViewSet):
    queryset = LoanExtension.objects.all()
    serializer_class = LoanExtensionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['application']
    ordering_fields = ['created_at']

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'stage', 'borrower', 'broker', 'product']
    search_fields = ['borrower__first_name', 'borrower__last_name', 'borrower__email']
    ordering_fields = ['created_at', 'updated_at', 'status', 'stage']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ApplicationDetailSerializer
        return ApplicationSerializer
    
    @action(detail=True, methods=['post'])
    def transition(self, request, pk=None):
        application = self.get_object()
        new_stage = request.data.get('stage')
        new_status = request.data.get('status')
        
        if new_stage and new_stage in dict(Application.STAGE_CHOICES).keys():
            application.stage = new_stage
        
        if new_status and new_status in dict(Application.STATUS_CHOICES).keys():
            application.status = new_status
            
        application.save()
        serializer = self.get_serializer(application)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        application = self.get_object()
        # Create a new application with the same data
        application.pk = None
        application.status = 'draft'
        application.save()
        
        serializer = self.get_serializer(application)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
