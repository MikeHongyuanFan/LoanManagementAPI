"""
Tests for dashboard models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from dashboard.models import (
    DashboardMetric,
    DashboardWidget,
    DashboardLayout,
    DashboardWidgetPlacement,
    UserDashboardPreference
)

User = get_user_model()


class DashboardModelTestCase(TestCase):
    """
    Test case for dashboard models
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
    
    def test_dashboard_metric_creation(self):
        """
        Test creating a dashboard metric
        """
        metric = DashboardMetric.objects.create(
            name='test_metric',
            display_name='Test Metric',
            description='Test metric description',
            category='application',
            metric_type='count',
            value=100
        )
        
        self.assertEqual(metric.name, 'test_metric')
        self.assertEqual(metric.display_name, 'Test Metric')
        self.assertEqual(metric.category, 'application')
        self.assertEqual(float(metric.value), 100.0)
        self.assertEqual(str(metric), 'Test Metric (application)')
    
    def test_dashboard_widget_creation(self):
        """
        Test creating a dashboard widget
        """
        widget = DashboardWidget.objects.create(
            name='test_widget',
            display_name='Test Widget',
            description='Test widget description',
            widget_type='chart_bar',
            configuration={'title': 'Test Chart', 'height': 300},
            created_by=self.user
        )
        
        self.assertEqual(widget.name, 'test_widget')
        self.assertEqual(widget.display_name, 'Test Widget')
        self.assertEqual(widget.widget_type, 'chart_bar')
        self.assertEqual(widget.configuration['title'], 'Test Chart')
        self.assertEqual(str(widget), 'Test Widget')
    
    def test_dashboard_layout_creation(self):
        """
        Test creating a dashboard layout
        """
        layout = DashboardLayout.objects.create(
            name='test_layout',
            description='Test layout description',
            is_default=True,
            created_by=self.user
        )
        
        self.assertEqual(layout.name, 'test_layout')
        self.assertEqual(layout.description, 'Test layout description')
        self.assertTrue(layout.is_default)
        self.assertEqual(layout.created_by, self.user)
        self.assertEqual(str(layout), 'test_layout')
    
    def test_widget_placement(self):
        """
        Test widget placement in layout
        """
        # Create widget and layout
        widget = DashboardWidget.objects.create(
            name='test_widget',
            display_name='Test Widget',
            widget_type='chart_bar',
            created_by=self.user
        )
        
        layout = DashboardLayout.objects.create(
            name='test_layout',
            created_by=self.user
        )
        
        # Add widget to layout
        placement = DashboardWidgetPlacement.objects.create(
            dashboard=layout,
            widget=widget,
            position_x=1,
            position_y=2,
            width=2,
            height=1
        )
        
        self.assertEqual(placement.dashboard, layout)
        self.assertEqual(placement.widget, widget)
        self.assertEqual(placement.position_x, 1)
        self.assertEqual(placement.position_y, 2)
        self.assertEqual(placement.width, 2)
        self.assertEqual(placement.height, 1)
        
        # Check that widget is in layout
        self.assertIn(widget, layout.widgets.all())
    
    def test_user_dashboard_preference(self):
        """
        Test user dashboard preference
        """
        # Create layout
        layout = DashboardLayout.objects.create(
            name='test_layout',
            created_by=self.user
        )
        
        # Create user preference
        preference = UserDashboardPreference.objects.create(
            user=self.user,
            layout=layout,
            custom_settings={'theme': 'dark', 'refresh_interval': 60}
        )
        
        self.assertEqual(preference.user, self.user)
        self.assertEqual(preference.layout, layout)
        self.assertEqual(preference.custom_settings['theme'], 'dark')
        self.assertEqual(preference.custom_settings['refresh_interval'], 60)
        self.assertEqual(str(preference), "testuser's Dashboard Preferences")
    
    def test_metric_with_json_value(self):
        """
        Test metric with JSON value
        """
        json_data = {
            'pending': 10,
            'approved': 20,
            'rejected': 5
        }
        
        metric = DashboardMetric.objects.create(
            name='status_distribution',
            display_name='Status Distribution',
            category='application',
            metric_type='custom',
            json_value=json_data
        )
        
        self.assertEqual(metric.json_value['pending'], 10)
        self.assertEqual(metric.json_value['approved'], 20)
        self.assertEqual(metric.json_value['rejected'], 5)
    
    def test_widget_with_multiple_metrics(self):
        """
        Test widget with multiple metrics
        """
        # Create metrics
        metric1 = DashboardMetric.objects.create(
            name='metric1',
            display_name='Metric 1',
            category='application',
            metric_type='count',
            value=100
        )
        
        metric2 = DashboardMetric.objects.create(
            name='metric2',
            display_name='Metric 2',
            category='document',
            metric_type='percentage',
            value=75.5
        )
        
        # Create widget
        widget = DashboardWidget.objects.create(
            name='test_widget',
            display_name='Test Widget',
            widget_type='chart_bar',
            created_by=self.user
        )
        
        # Add metrics to widget
        widget.metrics.add(metric1, metric2)
        
        self.assertEqual(widget.metrics.count(), 2)
        self.assertIn(metric1, widget.metrics.all())
        self.assertIn(metric2, widget.metrics.all())
