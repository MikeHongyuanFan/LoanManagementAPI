from django.db.models import Count, Avg, Sum, F, Q
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
import logging

from .models import (
    DashboardMetric, 
    DashboardWidget, 
    DashboardLayout, 
    UserDashboardPreference
)
from .serializers import (
    DashboardMetricSerializer,
    DashboardWidgetSerializer,
    DashboardLayoutSerializer,
    UserDashboardPreferenceSerializer,
    DashboardOverviewSerializer
)
from .cache import get_cached_dashboard_data, cache_dashboard_data

# Import models from other apps for data aggregation
from applications.models import Application
from documents.models import Document
from borrowers.models import Borrower
from brokers.models import Broker
from products.models import Product

# Set up logger
logger = logging.getLogger('dashboard')


class DashboardMetricViewSet(viewsets.ModelViewSet):
    """
    API endpoint for dashboard metrics
    """
    queryset = DashboardMetric.objects.all()
    serializer_class = DashboardMetricSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = DashboardMetric.objects.filter(is_active=True)
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        return queryset


class DashboardWidgetViewSet(viewsets.ModelViewSet):
    """
    API endpoint for dashboard widgets
    """
    queryset = DashboardWidget.objects.all()
    serializer_class = DashboardWidgetSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = DashboardWidget.objects.filter(is_active=True)
        widget_type = self.request.query_params.get('widget_type', None)
        if widget_type:
            queryset = queryset.filter(widget_type=widget_type)
        return queryset


class DashboardLayoutViewSet(viewsets.ModelViewSet):
    """
    API endpoint for dashboard layouts
    """
    queryset = DashboardLayout.objects.all()
    serializer_class = DashboardLayoutSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        # Return layouts created by the user or default layouts
        return DashboardLayout.objects.filter(
            Q(created_by=user) | Q(is_default=True)
        )
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class UserDashboardPreferenceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user dashboard preferences
    """
    queryset = UserDashboardPreference.objects.all()
    serializer_class = UserDashboardPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserDashboardPreference.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DashboardOverviewAPI(APIView):
    """
    API endpoint for dashboard overview data
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, format=None):
        # Get time range from query params (default to last 30 days)
        days = int(request.query_params.get('days', 30))
        
        # Try to get cached data first
        cache_params = {'days': days}
        cached_data = get_cached_dashboard_data('overview', cache_params)
        if cached_data:
            logger.info("Serving dashboard overview from cache")
            return Response(cached_data)
        
        logger.info("Generating dashboard overview data")
        start_time = timezone.now()
        
        start_date = timezone.now() - timezone.timedelta(days=days)
        
        # Loan Application Metrics
        loan_applications = {
            'total_applications': Application.objects.count(),
            'applications_by_status': dict(
                Application.objects.values('status').annotate(count=Count('id')).values_list('status', 'count')
            ),
            'applications_by_product': dict(
                Application.objects.values('product__name').annotate(count=Count('id')).values_list('product__name', 'count')
            ),
            'average_processing_time': Application.objects.filter(
                status='approved'
            ).aggregate(avg_time=Avg(F('updated_at') - F('created_at')))['avg_time'] or 0,
            'total_loan_amount': Application.objects.aggregate(total=Sum('gross_loan_amount'))['total'] or 0,
        }
        
        # Document Metrics
        documents = {
            'total_documents': Document.objects.count(),
            'documents_by_type': dict(
                Document.objects.values('document_type').annotate(count=Count('id')).values_list('document_type', 'count')
            ),
            'documents_by_status': dict(
                Document.objects.values('status').annotate(count=Count('id')).values_list('status', 'count')
            ),
            'documents_pending_approval': Document.objects.filter(status='pending_approval').count(),
            'documents_pending_signature': Document.objects.filter(status='pending_signature').count(),
        }
        
        # Borrower Metrics
        borrowers = {
            'total_borrowers': Borrower.objects.count(),
            'borrowers_by_state': dict(
                Borrower.objects.values('state').annotate(count=Count('id')).values_list('state', 'count')
            ),
            'new_borrowers_last_30_days': Borrower.objects.filter(created_at__gte=start_date).count(),
        }
        
        # Broker Metrics
        brokers = {
            'total_brokers': Broker.objects.count(),
            'new_brokers_last_30_days': Broker.objects.filter(created_at__gte=start_date).count(),
        }
        
        # Product Metrics
        products = {
            'total_products': Product.objects.count(),
            'products_by_usage': dict(
                Application.objects.values('product__name').annotate(count=Count('id')).values_list('product__name', 'count')
            ),
        }
        
        # Combine all metrics
        overview_data = {
            'loan_applications': loan_applications,
            'documents': documents,
            'borrowers': borrowers,
            'brokers': brokers,
            'products': products,
            'last_updated': timezone.now(),
        }
        
        # Calculate generation time
        generation_time = (timezone.now() - start_time).total_seconds()
        logger.info(f"Dashboard overview data generated in {generation_time:.3f}s")
        
        # Cache the data
        serializer = DashboardOverviewSerializer(overview_data)
        cache_dashboard_data('overview', serializer.data, cache_params)
        
        return Response(serializer.data)


class ApplicationDashboardAPI(APIView):
    """
    API endpoint for application-specific dashboard data
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, format=None):
        # Get time range from query params (default to last 30 days)
        days = int(request.query_params.get('days', 30))
        
        # Try to get cached data first
        cache_params = {'days': days}
        cached_data = get_cached_dashboard_data('applications', cache_params)
        if cached_data:
            logger.info("Serving application dashboard from cache")
            return Response(cached_data)
        
        logger.info("Generating application dashboard data")
        start_time = timezone.now()
        
        start_date = timezone.now() - timezone.timedelta(days=days)
        
        # Applications over time (grouped by day)
        applications_over_time = Application.objects.filter(
            created_at__gte=start_date
        ).extra(
            select={'date': "DATE(created_at)"}
        ).values('date').annotate(count=Count('id')).order_by('date')
        
        # Applications by status
        applications_by_status = Application.objects.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Applications by product
        applications_by_product = Application.objects.values(
            'product__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Top brokers by application count
        top_brokers = Application.objects.values(
            'broker__id', 'broker__first_name', 'broker__last_name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Loan amount distribution
        loan_amount_ranges = [
            {'min': 0, 'max': 100000, 'label': '0-100K'},
            {'min': 100000, 'max': 250000, 'label': '100K-250K'},
            {'min': 250000, 'max': 500000, 'label': '250K-500K'},
            {'min': 500000, 'max': 1000000, 'label': '500K-1M'},
            {'min': 1000000, 'max': float('inf'), 'label': '1M+'},
        ]
        
        loan_amount_distribution = []
        for range_info in loan_amount_ranges:
            count = Application.objects.filter(
                gross_loan_amount__gte=range_info['min'],
                gross_loan_amount__lt=range_info['max']
            ).count()
            loan_amount_distribution.append({
                'label': range_info['label'],
                'count': count
            })
        
        # Combine all metrics
        dashboard_data = {
            'applications_over_time': list(applications_over_time),
            'applications_by_status': list(applications_by_status),
            'applications_by_product': list(applications_by_product),
            'top_brokers': list(top_brokers),
            'loan_amount_distribution': loan_amount_distribution,
            'last_updated': timezone.now(),
        }
        
        # Calculate generation time
        generation_time = (timezone.now() - start_time).total_seconds()
        logger.info(f"Application dashboard data generated in {generation_time:.3f}s")
        
        # Cache the data
        cache_dashboard_data('applications', dashboard_data, cache_params)
        
        return Response(dashboard_data)


class DocumentDashboardAPI(APIView):
    """
    API endpoint for document-specific dashboard data
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, format=None):
        # Get time range from query params (default to last 30 days)
        days = int(request.query_params.get('days', 30))
        
        # Try to get cached data first
        cache_params = {'days': days}
        cached_data = get_cached_dashboard_data('documents', cache_params)
        if cached_data:
            logger.info("Serving document dashboard from cache")
            return Response(cached_data)
        
        logger.info("Generating document dashboard data")
        start_time = timezone.now()
        
        start_date = timezone.now() - timezone.timedelta(days=days)
        
        # Documents over time (grouped by day)
        documents_over_time = Document.objects.filter(
            created_at__gte=start_date
        ).extra(
            select={'date': "DATE(created_at)"}
        ).values('date').annotate(count=Count('id')).order_by('date')
        
        # Documents by type
        documents_by_type = Document.objects.values('document_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Documents by status
        documents_by_status = Document.objects.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Documents by category
        documents_by_category = Document.objects.values(
            'category__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Approval metrics
        approval_metrics = {
            'pending_approval': Document.objects.filter(status='pending_approval').count(),
            'approved': Document.objects.filter(status='approved').count(),
            'rejected': Document.objects.filter(status='rejected').count(),
            'average_approval_time': 0,  # This would require more complex calculation
        }
        
        # Signature metrics
        signature_metrics = {
            'pending_signature': Document.objects.filter(status='pending_signature').count(),
            'signed': Document.objects.filter(status='signed').count(),
            'declined': Document.objects.filter(status='signature_declined').count(),
            'average_signature_time': 0,  # This would require more complex calculation
        }
        
        # Combine all metrics
        dashboard_data = {
            'documents_over_time': list(documents_over_time),
            'documents_by_type': list(documents_by_type),
            'documents_by_status': list(documents_by_status),
            'documents_by_category': list(documents_by_category),
            'approval_metrics': approval_metrics,
            'signature_metrics': signature_metrics,
            'last_updated': timezone.now(),
        }
        
        # Calculate generation time
        generation_time = (timezone.now() - start_time).total_seconds()
        logger.info(f"Document dashboard data generated in {generation_time:.3f}s")
        
        # Cache the data
        cache_dashboard_data('documents', dashboard_data, cache_params)
        
        return Response(dashboard_data)


class BorrowerBrokerDashboardAPI(APIView):
    """
    API endpoint for borrower and broker dashboard data
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, format=None):
        # Get time range from query params (default to last 30 days)
        days = int(request.query_params.get('days', 30))
        
        # Try to get cached data first
        cache_params = {'days': days}
        cached_data = get_cached_dashboard_data('entities', cache_params)
        if cached_data:
            logger.info("Serving entity dashboard from cache")
            return Response(cached_data)
        
        logger.info("Generating entity dashboard data")
        start_time = timezone.now()
        
        start_date = timezone.now() - timezone.timedelta(days=days)
        
        # Borrowers over time
        borrowers_over_time = Borrower.objects.filter(
            created_at__gte=start_date
        ).extra(
            select={'date': "DATE(created_at)"}
        ).values('date').annotate(count=Count('id')).order_by('date')
        
        # Borrowers by state
        borrowers_by_state = Borrower.objects.values('state').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Brokers over time
        brokers_over_time = Broker.objects.filter(
            created_at__gte=start_date
        ).extra(
            select={'date': "DATE(created_at)"}
        ).values('date').annotate(count=Count('id')).order_by('date')
        
        # Top borrowers by loan amount
        top_borrowers = Application.objects.values(
            'borrower__id', 'borrower__first_name', 'borrower__last_name'
        ).annotate(
            total_loan_amount=Sum('gross_loan_amount'),
            application_count=Count('id')
        ).order_by('-total_loan_amount')[:10]
        
        # Top brokers by loan amount
        top_brokers = Application.objects.values(
            'broker__id', 'broker__first_name', 'broker__last_name'
        ).annotate(
            total_loan_amount=Sum('gross_loan_amount'),
            application_count=Count('id')
        ).order_by('-total_loan_amount')[:10]
        
        # Combine all metrics
        dashboard_data = {
            'borrowers_over_time': list(borrowers_over_time),
            'borrowers_by_state': list(borrowers_by_state),
            'brokers_over_time': list(brokers_over_time),
            'top_borrowers': list(top_borrowers),
            'top_brokers': list(top_brokers),
            'last_updated': timezone.now(),
        }
        
        # Calculate generation time
        generation_time = (timezone.now() - start_time).total_seconds()
        logger.info(f"Entity dashboard data generated in {generation_time:.3f}s")
        
        # Cache the data
        cache_dashboard_data('entities', dashboard_data, cache_params)
        
        return Response(dashboard_data)
