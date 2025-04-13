"""
Services for dashboard data aggregation and processing
"""
from django.db.models import Count, Avg, Sum, F, Q
from django.utils import timezone
from datetime import timedelta

from applications.models import Application
from documents.models import Document
from borrowers.models import Borrower
from brokers.models import Broker
from products.models import Product
from .models import DashboardMetric


class MetricAggregationService:
    """
    Service for aggregating metrics from various data sources
    """
    
    @staticmethod
    def update_application_metrics():
        """
        Update application-related metrics
        """
        # Total applications
        DashboardMetric.objects.update_or_create(
            name='total_applications',
            category='application',
            defaults={
                'display_name': 'Total Applications',
                'description': 'Total number of loan applications',
                'metric_type': 'count',
                'value': Application.objects.count(),
            }
        )
        
        # Applications by status
        status_counts = dict(
            Application.objects.values('status').annotate(count=Count('id')).values_list('status', 'count')
        )
        
        DashboardMetric.objects.update_or_create(
            name='applications_by_status',
            category='application',
            defaults={
                'display_name': 'Applications by Status',
                'description': 'Distribution of applications by status',
                'metric_type': 'custom',
                'json_value': status_counts,
            }
        )
        
        # Total loan amount
        total_loan_amount = Application.objects.aggregate(total=Sum('loan_amount'))['total'] or 0
        
        DashboardMetric.objects.update_or_create(
            name='total_loan_amount',
            category='application',
            defaults={
                'display_name': 'Total Loan Amount',
                'description': 'Sum of all loan amounts',
                'metric_type': 'currency',
                'value': total_loan_amount,
            }
        )
        
        # Applications in last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_apps_count = Application.objects.filter(created_at__gte=thirty_days_ago).count()
        
        DashboardMetric.objects.update_or_create(
            name='recent_applications',
            category='application',
            defaults={
                'display_name': 'Recent Applications (30 days)',
                'description': 'Applications created in the last 30 days',
                'metric_type': 'count',
                'value': recent_apps_count,
            }
        )
    
    @staticmethod
    def update_document_metrics():
        """
        Update document-related metrics
        """
        # Total documents
        DashboardMetric.objects.update_or_create(
            name='total_documents',
            category='document',
            defaults={
                'display_name': 'Total Documents',
                'description': 'Total number of documents',
                'metric_type': 'count',
                'value': Document.objects.count(),
            }
        )
        
        # Documents by type
        type_counts = dict(
            Document.objects.values('document_type').annotate(count=Count('id')).values_list('document_type', 'count')
        )
        
        DashboardMetric.objects.update_or_create(
            name='documents_by_type',
            category='document',
            defaults={
                'display_name': 'Documents by Type',
                'description': 'Distribution of documents by type',
                'metric_type': 'custom',
                'json_value': type_counts,
            }
        )
        
        # Documents pending approval
        pending_approval = Document.objects.filter(status='pending_approval').count()
        
        DashboardMetric.objects.update_or_create(
            name='documents_pending_approval',
            category='document',
            defaults={
                'display_name': 'Documents Pending Approval',
                'description': 'Number of documents awaiting approval',
                'metric_type': 'count',
                'value': pending_approval,
            }
        )
        
        # Documents pending signature
        pending_signature = Document.objects.filter(status='pending_signature').count()
        
        DashboardMetric.objects.update_or_create(
            name='documents_pending_signature',
            category='document',
            defaults={
                'display_name': 'Documents Pending Signature',
                'description': 'Number of documents awaiting signature',
                'metric_type': 'count',
                'value': pending_signature,
            }
        )
    
    @staticmethod
    def update_borrower_metrics():
        """
        Update borrower-related metrics
        """
        # Total borrowers
        DashboardMetric.objects.update_or_create(
            name='total_borrowers',
            category='borrower',
            defaults={
                'display_name': 'Total Borrowers',
                'description': 'Total number of borrowers',
                'metric_type': 'count',
                'value': Borrower.objects.count(),
            }
        )
        
        # Active borrowers
        active_borrowers = Borrower.objects.filter(is_active=True).count()
        
        DashboardMetric.objects.update_or_create(
            name='active_borrowers',
            category='borrower',
            defaults={
                'display_name': 'Active Borrowers',
                'description': 'Number of active borrowers',
                'metric_type': 'count',
                'value': active_borrowers,
            }
        )
        
        # New borrowers in last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        new_borrowers = Borrower.objects.filter(created_at__gte=thirty_days_ago).count()
        
        DashboardMetric.objects.update_or_create(
            name='new_borrowers',
            category='borrower',
            defaults={
                'display_name': 'New Borrowers (30 days)',
                'description': 'Borrowers created in the last 30 days',
                'metric_type': 'count',
                'value': new_borrowers,
            }
        )
    
    @staticmethod
    def update_broker_metrics():
        """
        Update broker-related metrics
        """
        # Total brokers
        DashboardMetric.objects.update_or_create(
            name='total_brokers',
            category='broker',
            defaults={
                'display_name': 'Total Brokers',
                'description': 'Total number of brokers',
                'metric_type': 'count',
                'value': Broker.objects.count(),
            }
        )
        
        # Active brokers
        active_brokers = Broker.objects.filter(is_active=True).count()
        
        DashboardMetric.objects.update_or_create(
            name='active_brokers',
            category='broker',
            defaults={
                'display_name': 'Active Brokers',
                'description': 'Number of active brokers',
                'metric_type': 'count',
                'value': active_brokers,
            }
        )
        
        # New brokers in last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        new_brokers = Broker.objects.filter(created_at__gte=thirty_days_ago).count()
        
        DashboardMetric.objects.update_or_create(
            name='new_brokers',
            category='broker',
            defaults={
                'display_name': 'New Brokers (30 days)',
                'description': 'Brokers created in the last 30 days',
                'metric_type': 'count',
                'value': new_brokers,
            }
        )
    
    @staticmethod
    def update_product_metrics():
        """
        Update product-related metrics
        """
        # Total products
        DashboardMetric.objects.update_or_create(
            name='total_products',
            category='product',
            defaults={
                'display_name': 'Total Products',
                'description': 'Total number of loan products',
                'metric_type': 'count',
                'value': Product.objects.count(),
            }
        )
        
        # Active products
        active_products = Product.objects.filter(is_active=True).count()
        
        DashboardMetric.objects.update_or_create(
            name='active_products',
            category='product',
            defaults={
                'display_name': 'Active Products',
                'description': 'Number of active loan products',
                'metric_type': 'count',
                'value': active_products,
            }
        )
        
        # Average interest rate
        avg_rate = Product.objects.aggregate(avg=Avg('base_interest_rate'))['avg'] or 0
        
        DashboardMetric.objects.update_or_create(
            name='average_interest_rate',
            category='product',
            defaults={
                'display_name': 'Average Interest Rate',
                'description': 'Average base interest rate across all products',
                'metric_type': 'percentage',
                'value': avg_rate,
            }
        )
    
    @staticmethod
    def update_all_metrics():
        """
        Update all metrics
        """
        MetricAggregationService.update_application_metrics()
        MetricAggregationService.update_document_metrics()
        MetricAggregationService.update_borrower_metrics()
        MetricAggregationService.update_broker_metrics()
        MetricAggregationService.update_product_metrics()
