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
    
    @classmethod
    def _update_or_create_metric(cls, name, display_name, category, metric_type, value=None, json_value=None):
        """
        Helper method to update or create a metric
        """
        DashboardMetric.objects.update_or_create(
            name=name,
            category=category,
            defaults={
                'display_name': display_name,
                'description': f'{display_name} metric',
                'metric_type': metric_type,
                'value': value,
                'json_value': json_value,
            }
        )
    
    @classmethod
    def update_application_metrics(cls):
        """
        Update application-related metrics
        """
        # Total applications
        total_applications = Application.objects.count()
        cls._update_or_create_metric('total_applications', 'Total Applications', 'application', 'count', total_applications)
        
        # Applications by status
        status_counts = dict(
            Application.objects.values('status').annotate(count=Count('id')).values_list('status', 'count')
        )
        cls._update_or_create_metric('applications_by_status', 'Applications by Status', 'application', 'custom', json_value=status_counts)
        
        # Applications in last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_apps_count = Application.objects.filter(created_at__gte=thirty_days_ago).count()
        cls._update_or_create_metric('recent_applications', 'Recent Applications (30 days)', 'application', 'count', recent_apps_count)
    
    @classmethod
    def update_document_metrics(cls):
        """
        Update document-related metrics
        """
        # Total documents
        total_documents = Document.objects.count()
        cls._update_or_create_metric('total_documents', 'Total Documents', 'document', 'count', total_documents)
        
        # Documents by type
        type_counts = dict(
            Document.objects.values('document_type').annotate(count=Count('id')).values_list('document_type', 'count')
        )
        cls._update_or_create_metric('documents_by_type', 'Documents by Type', 'document', 'custom', json_value=type_counts)
        
        # Documents pending approval
        pending_approval = Document.objects.filter(status='pending_approval').count()
        cls._update_or_create_metric('documents_pending_approval', 'Documents Pending Approval', 'document', 'count', pending_approval)
        
        # Documents pending signature
        pending_signature = Document.objects.filter(status='pending_signature').count()
        cls._update_or_create_metric('documents_pending_signature', 'Documents Pending Signature', 'document', 'count', pending_signature)
    
    @classmethod
    def update_borrower_metrics(cls):
        """
        Update borrower-related metrics
        """
        # Total borrowers
        total_borrowers = Borrower.objects.count()
        cls._update_or_create_metric('total_borrowers', 'Total Borrowers', 'borrower', 'count', total_borrowers)
        
        # New borrowers in last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        new_borrowers = Borrower.objects.filter(created_at__gte=thirty_days_ago).count()
        cls._update_or_create_metric('new_borrowers', 'New Borrowers (30 days)', 'borrower', 'count', new_borrowers)
    
    @classmethod
    def update_broker_metrics(cls):
        """
        Update broker-related metrics
        """
        # Total brokers
        total_brokers = Broker.objects.count()
        cls._update_or_create_metric('total_brokers', 'Total Brokers', 'broker', 'count', total_brokers)
        
        # New brokers in last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        new_brokers = Broker.objects.filter(created_at__gte=thirty_days_ago).count()
        cls._update_or_create_metric('new_brokers', 'New Brokers (30 days)', 'broker', 'count', new_brokers)
    
    @classmethod
    def update_product_metrics(cls):
        """
        Update product-related metrics
        """
        # Total products
        total_products = Product.objects.count()
        cls._update_or_create_metric('total_products', 'Total Products', 'product', 'count', total_products)
        
        # Products by usage
        products_by_usage = dict(
            Application.objects.values('product__name').annotate(count=Count('id')).values_list('product__name', 'count')
        )
        cls._update_or_create_metric('products_by_usage', 'Products by Usage', 'product', 'custom', json_value=products_by_usage)
    
    @classmethod
    def update_all_metrics(cls):
        """
        Update all metrics
        """
        cls.update_application_metrics()
        cls.update_document_metrics()
        cls.update_borrower_metrics()
        cls.update_broker_metrics()
        cls.update_product_metrics()
