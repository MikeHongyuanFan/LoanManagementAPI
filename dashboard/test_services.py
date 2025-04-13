"""
Tests for dashboard services
"""
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta

from applications.models import Application
from documents.models import Document
from borrowers.models import Borrower
from brokers.models import Broker
from products.models import Product

from dashboard.models import DashboardMetric
from dashboard.services import MetricAggregationService

User = get_user_model()


class MetricAggregationServiceTestCase(TestCase):
    """
    Test case for metric aggregation service
    """
    
    def setUp(self):
        """
        Set up test data
        """
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create test product
        self.product = Product.objects.create(
            name='Test Product',
            description='Test product description'
        )
        
        # Create test borrower
        self.borrower = Borrower.objects.create(
            first_name='Test',
            last_name='Borrower',
            email='borrower@example.com',
            state='CA',
            dob='1990-01-01',
            phone_number='1234567890'
        )
        
        # Create test broker
        self.broker = Broker.objects.create(
            first_name='Test',
            last_name='Broker',
            email='broker@example.com',
            phone_number='1234567890'
        )
        
        # Create test application
        self.application = Application.objects.create(
            borrower=self.borrower,
            broker=self.broker,
            product=self.product,
            gross_loan_amount=250000,
            net_loan_amount=240000,
            status='pending',
            stage='application'
        )
        
        # Create test document
        self.document = Document.objects.create(
            title='Test Document',
            document_type='application',
            status='pending_approval',
            uploaded_by=self.user
        )
    
    def test_update_application_metrics(self):
        """
        Test updating application metrics
        """
        # Run the service method
        MetricAggregationService.update_application_metrics()
        
        # Check that metrics were created
        self.assertTrue(DashboardMetric.objects.filter(name='total_applications').exists())
        self.assertTrue(DashboardMetric.objects.filter(name='applications_by_status').exists())
        
        # Check metric values
        total_apps = DashboardMetric.objects.get(name='total_applications')
        self.assertEqual(float(total_apps.value), 1.0)
        
        # Create another application
        Application.objects.create(
            borrower=self.borrower,
            broker=self.broker,
            product=self.product,
            gross_loan_amount=150000,
            net_loan_amount=145000,
            status='approved',
            stage='approved'
        )
        
        # Run the service method again
        MetricAggregationService.update_application_metrics()
        
        # Check that metrics were updated
        total_apps = DashboardMetric.objects.get(name='total_applications')
        self.assertEqual(float(total_apps.value), 2.0)
        
        # Check status distribution
        status_distribution = DashboardMetric.objects.get(name='applications_by_status')
        self.assertEqual(status_distribution.json_value['pending'], 1)
        self.assertEqual(status_distribution.json_value['approved'], 1)
    
    def test_update_document_metrics(self):
        """
        Test updating document metrics
        """
        # Run the service method
        MetricAggregationService.update_document_metrics()
        
        # Check that metrics were created
        self.assertTrue(DashboardMetric.objects.filter(name='total_documents').exists())
        self.assertTrue(DashboardMetric.objects.filter(name='documents_by_type').exists())
        self.assertTrue(DashboardMetric.objects.filter(name='documents_pending_approval').exists())
        
        # Check metric values
        total_docs = DashboardMetric.objects.get(name='total_documents')
        self.assertEqual(float(total_docs.value), 1.0)
        
        pending_approval = DashboardMetric.objects.get(name='documents_pending_approval')
        self.assertEqual(float(pending_approval.value), 1.0)
        
        # Create another document
        Document.objects.create(
            title='Another Document',
            document_type='contract',
            status='approved',
            uploaded_by=self.user
        )
        
        # Run the service method again
        MetricAggregationService.update_document_metrics()
        
        # Check that metrics were updated
        total_docs = DashboardMetric.objects.get(name='total_documents')
        self.assertEqual(float(total_docs.value), 2.0)
        
        # Check type distribution
        type_distribution = DashboardMetric.objects.get(name='documents_by_type')
        self.assertEqual(type_distribution.json_value['application'], 1)
        self.assertEqual(type_distribution.json_value['contract'], 1)
    
    def test_update_borrower_metrics(self):
        """
        Test updating borrower metrics
        """
        # Run the service method
        MetricAggregationService.update_borrower_metrics()
        
        # Check that metrics were created
        self.assertTrue(DashboardMetric.objects.filter(name='total_borrowers').exists())
        
        # Check metric values
        total_borrowers = DashboardMetric.objects.get(name='total_borrowers')
        self.assertEqual(float(total_borrowers.value), 1.0)
        
        # Create another borrower
        Borrower.objects.create(
            first_name='Another',
            last_name='Borrower',
            email='another@example.com',
            state='NY',
            dob='1985-05-15',
            phone_number='9876543210'
        )
        
        # Run the service method again
        MetricAggregationService.update_borrower_metrics()
        
        # Check that metrics were updated
        total_borrowers = DashboardMetric.objects.get(name='total_borrowers')
        self.assertEqual(float(total_borrowers.value), 2.0)
    
    def test_update_broker_metrics(self):
        """
        Test updating broker metrics
        """
        # Run the service method
        MetricAggregationService.update_broker_metrics()
        
        # Check that metrics were created
        self.assertTrue(DashboardMetric.objects.filter(name='total_brokers').exists())
        
        # Check metric values
        total_brokers = DashboardMetric.objects.get(name='total_brokers')
        self.assertEqual(float(total_brokers.value), 1.0)
    
    def test_update_product_metrics(self):
        """
        Test updating product metrics
        """
        # Run the service method
        MetricAggregationService.update_product_metrics()
        
        # Check that metrics were created
        self.assertTrue(DashboardMetric.objects.filter(name='total_products').exists())
        
        # Check metric values
        total_products = DashboardMetric.objects.get(name='total_products')
        self.assertEqual(float(total_products.value), 1.0)
        
        # Create another product
        Product.objects.create(
            name='Another Product',
            description='Another product description'
        )
        
        # Run the service method again
        MetricAggregationService.update_product_metrics()
        
        # Check that metrics were updated
        total_products = DashboardMetric.objects.get(name='total_products')
        self.assertEqual(float(total_products.value), 2.0)
    
    def test_update_all_metrics(self):
        """
        Test updating all metrics
        """
        # Run the service method
        MetricAggregationService.update_all_metrics()
        
        # Check that all metrics were created
        self.assertTrue(DashboardMetric.objects.filter(name='total_applications').exists())
        self.assertTrue(DashboardMetric.objects.filter(name='total_documents').exists())
        self.assertTrue(DashboardMetric.objects.filter(name='total_borrowers').exists())
        self.assertTrue(DashboardMetric.objects.filter(name='total_brokers').exists())
        self.assertTrue(DashboardMetric.objects.filter(name='total_products').exists())
