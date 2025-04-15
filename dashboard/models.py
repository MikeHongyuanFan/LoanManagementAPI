from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class DashboardMetric(models.Model):
    """
    Model to store pre-calculated metrics for dashboard display
    """
    METRIC_TYPES = (
        ('count', 'Count'),
        ('percentage', 'Percentage'),
        ('currency', 'Currency'),
        ('duration', 'Duration'),
        ('custom', 'Custom'),
    )
    
    CATEGORIES = (
        ('application', 'Loan Application'),
        ('document', 'Document Management'),
        ('borrower', 'Borrower'),
        ('broker', 'Broker'),
        ('product', 'Product'),
        ('system', 'System'),
    )
    
    name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES)
    value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    string_value = models.CharField(max_length=255, null=True, blank=True)
    json_value = models.JSONField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.display_name} ({self.category})"
    
    class Meta:
        ordering = ['category', 'name']
        unique_together = ['name', 'category']


class DashboardWidget(models.Model):
    """
    Model to define dashboard widgets and their configuration
    """
    WIDGET_TYPES = (
        ('chart_line', 'Line Chart'),
        ('chart_bar', 'Bar Chart'),
        ('chart_pie', 'Pie Chart'),
        ('chart_doughnut', 'Doughnut Chart'),
        ('stat_card', 'Statistic Card'),
        ('table', 'Table'),
        ('list', 'List'),
        ('custom', 'Custom'),
    )
    
    name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES)
    metrics = models.ManyToManyField(DashboardMetric, related_name='widgets')
    configuration = models.JSONField(default=dict)
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    width = models.IntegerField(default=1)
    height = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_widgets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.display_name
    
    class Meta:
        ordering = ['position_y', 'position_x']


class DashboardLayout(models.Model):
    """
    Model to store dashboard layouts for different users or roles
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    widgets = models.ManyToManyField(DashboardWidget, through='DashboardWidgetPlacement')
    is_default = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_layouts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-is_default', 'name']


class DashboardWidgetPlacement(models.Model):
    """
    Model to define the placement of widgets in a dashboard layout
    """
    dashboard = models.ForeignKey(DashboardLayout, on_delete=models.CASCADE)
    widget = models.ForeignKey(DashboardWidget, on_delete=models.CASCADE)
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    width = models.IntegerField(default=1)
    height = models.IntegerField(default=1)
    
    class Meta:
        ordering = ['position_y', 'position_x']
        unique_together = ['dashboard', 'widget']


class UserDashboardPreference(models.Model):
    """
    Model to store user preferences for dashboard layouts
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dashboard_preference')
    layout = models.ForeignKey(DashboardLayout, on_delete=models.SET_NULL, null=True)
    custom_settings = models.JSONField(default=dict)
    
    def __str__(self):
        return f"{self.user.username}'s Dashboard Preferences"
