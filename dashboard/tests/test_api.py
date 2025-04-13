"""
Tests for the dashboard API endpoints
"""
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
import json

from applications.models import Application
from documents.models import Document
from borrowers.models import Borrower
from brokers.models import Broker
from products.models import Product

from dashboard.models import (
    DashboardMetric,
    DashboardWidget,
    DashboardLayout,
    UserDashboardPreference
)
from dashboard.services import MetricAggregationService

User = get_user_model()


class DashboardAPITestCase(APITestCase):
    """
    Test case for dashboard API endpoints
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
        
        # Create test admin user
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpassword',
            is_staff=True
        )
        
        # Set up API client
        self.client = APIClient()
        
        # Create test metrics
        self.metric1 = DashboardMetric.objects.create(
            name='test_metric_1',
            display_name='Test Metric 1',
            description='Test metric 1 description',
            category='application',
            metric_type='count',
            value=100
        )
        
        self.metric2 = DashboardMetric.objects.create(
            name='test_metric_2',
            display_name='Test Metric 2',
            description='Test metric 2 description',
            category='document',
            metric_type='percentage',
            value=75.5
        )
        
        # Create test widget
        self.widget = DashboardWidget.objects.create(
            name='test_widget',
            display_name='Test Widget',
            description='Test widget description',
            widget_type='chart_bar',
            configuration={'title': 'Test Chart', 'height': 300},
            created_by=self.user
        )
        self.widget.metrics.add(self.metric1, self.metric2)
        
        # Create test layout
        self.layout = DashboardLayout.objects.create(
            name='test_layout',
            description='Test layout description',
            is_default=True,
            created_by=self.user
        )
        
        # Add widget to layout
        self.widget_placement = self.layout.dashboardwidgetplacement_set.create(
            widget=self.widget,
            position_x=0,
            position_y=0,
            width=2,
            height=1
        )
        
        # Create user preference
        self.preference = UserDashboardPreference.objects.create(
            user=self.user,
            layout=self.layout,
            custom_settings={'theme': 'dark'}
        )
    
    def test_metrics_list_authenticated(self):
        """
        Test that authenticated users can list metrics
        """
        self.client.force_authenticate(user=self.user)
        url = reverse('dashboardmetric-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_metrics_list_unauthenticated(self):
        """
        Test that unauthenticated users cannot list metrics
        """
        url = reverse('dashboardmetric-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_metrics_filter_by_category(self):
        """
        Test filtering metrics by category
        """
        self.client.force_authenticate(user=self.user)
        url = reverse('dashboardmetric-list')
        response = self.client.get(url, {'category': 'application'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'test_metric_1')
    
    def test_widgets_list(self):
        """
        Test listing widgets
        """
        self.client.force_authenticate(user=self.user)
        url = reverse('dashboardwidget-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'test_widget')
        self.assertEqual(len(response.data['results'][0]['metrics']), 2)
    
    def test_layouts_list(self):
        """
        Test listing layouts
        """
        self.client.force_authenticate(user=self.user)
        url = reverse('dashboardlayout-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'test_layout')
        self.assertEqual(len(response.data['results'][0]['widgets']), 1)
    
    def test_user_preference(self):
        """
        Test user preference retrieval
        """
        self.client.force_authenticate(user=self.user)
        url = reverse('userdashboardpreference-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['custom_settings']['theme'], 'dark')
    
    def test_dashboard_overview(self):
        """
        Test dashboard overview API
        """
        self.client.force_authenticate(user=self.user)
        url = reverse('dashboard-overview')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('loan_applications', response.data)
        self.assertIn('documents', response.data)
        self.assertIn('borrowers', response.data)
        self.assertIn('brokers', response.data)
        self.assertIn('products', response.data)
    
    def test_application_dashboard(self):
        """
        Test application dashboard API
        """
        self.client.force_authenticate(user=self.user)
        url = reverse('application-dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('applications_by_status', response.data)
        self.assertIn('applications_by_product', response.data)
        self.assertIn('loan_amount_distribution', response.data)
    
    def test_document_dashboard(self):
        """
        Test document dashboard API
        """
        self.client.force_authenticate(user=self.user)
        url = reverse('document-dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('documents_by_type', response.data)
        self.assertIn('documents_by_status', response.data)
        self.assertIn('approval_metrics', response.data)
    
    def test_entity_dashboard(self):
        """
        Test entity dashboard API
        """
        self.client.force_authenticate(user=self.user)
        url = reverse('entity-dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('borrowers_by_state', response.data)
        self.assertIn('brokers_by_company', response.data)
    
    def test_create_widget(self):
        """
        Test creating a new widget
        """
        self.client.force_authenticate(user=self.user)
        url = reverse('dashboardwidget-list')
        data = {
            'name': 'new_widget',
            'display_name': 'New Widget',
            'description': 'New widget description',
            'widget_type': 'chart_pie',
            'configuration': json.dumps({'title': 'New Chart', 'height': 400}),
            'position_x': 1,
            'position_y': 1,
            'width': 1,
            'height': 1
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'new_widget')
        self.assertEqual(response.data['widget_type'], 'chart_pie')
    
    def test_update_layout(self):
        """
        Test updating a layout
        """
        self.client.force_authenticate(user=self.user)
        url = reverse('dashboardlayout-detail', args=[self.layout.id])
        data = {
            'name': 'updated_layout',
            'description': 'Updated layout description'
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'updated_layout')
        self.assertEqual(response.data['description'], 'Updated layout description')
    
    def test_metric_aggregation_service(self):
        """
        Test metric aggregation service
        """
        # Create some test data
        product = Product.objects.create(
            name='Test Product',
            base_interest_rate=5.5,
            is_active=True
        )
        
        borrower = Borrower.objects.create(
            first_name='Test',
            last_name='Borrower',
            email='borrower@example.com',
            state='CA',
            is_active=True
        )
        
        broker = Broker.objects.create(
            first_name='Test',
            last_name='Broker',
            email='broker@example.com',
            company_name='Test Company',
            is_active=True
        )
        
        application = Application.objects.create(
            borrower=borrower,
            broker=broker,
            product=product,
            loan_amount=250000,
            status='pending'
        )
        
        document = Document.objects.create(
            title='Test Document',
            document_type='application',
            status='pending_approval',
            created_by=self.user
        )
        
        # Run metric aggregation
        MetricAggregationService.update_all_metrics()
        
        # Check that metrics were created
        self.assertTrue(DashboardMetric.objects.filter(name='total_applications').exists())
        self.assertTrue(DashboardMetric.objects.filter(name='total_documents').exists())
        self.assertTrue(DashboardMetric.objects.filter(name='total_borrowers').exists())
        self.assertTrue(DashboardMetric.objects.filter(name='total_brokers').exists())
        self.assertTrue(DashboardMetric.objects.filter(name='total_products').exists())
        
        # Check metric values
        total_apps = DashboardMetric.objects.get(name='total_applications')
        self.assertEqual(float(total_apps.value), 1.0)
        
        total_docs = DashboardMetric.objects.get(name='total_documents')
        self.assertEqual(float(total_docs.value), 1.0)
