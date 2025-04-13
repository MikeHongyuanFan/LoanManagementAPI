"""
Tests for dashboard performance
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
import time
import json

from applications.models import Application
from documents.models import Document
from borrowers.models import Borrower
from brokers.models import Broker
from products.models import Product

from dashboard.models import DashboardMetric
from dashboard.cache import get_cache_key, invalidate_dashboard_cache

User = get_user_model()


class DashboardPerformanceTestCase(TestCase):
    """
    Test case for dashboard performance
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
        
        # Set up client
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')
        
        # Clear cache
        cache.clear()
    
    def test_document_dashboard_performance(self):
        """
        Test performance of document dashboard API
        """
        url = reverse('document-dashboard')
        
        # First request (uncached)
        start_time = time.time()
        response1 = self.client.get(url)
        first_request_time = time.time() - start_time
        
        self.assertEqual(response1.status_code, 200)
        
        # Second request (should be cached)
        start_time = time.time()
        response2 = self.client.get(url)
        second_request_time = time.time() - start_time
        
        self.assertEqual(response2.status_code, 200)
        
        # Verify that the second request was faster
        self.assertLess(second_request_time, first_request_time)
    
    def test_performance_middleware(self):
        """
        Test performance middleware
        """
        url = reverse('document-dashboard')
        
        # Make a request
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check that the response has the performance header
        self.assertIn('X-Dashboard-Response-Time', response.headers)
        self.assertTrue(response.headers['X-Dashboard-Response-Time'].endswith('s'))
