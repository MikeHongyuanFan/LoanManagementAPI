from rest_framework import serializers
from .models import (
    DashboardMetric, 
    DashboardWidget, 
    DashboardLayout, 
    DashboardWidgetPlacement,
    UserDashboardPreference
)


class DashboardMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardMetric
        fields = '__all__'


class DashboardWidgetSerializer(serializers.ModelSerializer):
    metrics = DashboardMetricSerializer(many=True, read_only=True)
    
    class Meta:
        model = DashboardWidget
        fields = '__all__'


class DashboardWidgetPlacementSerializer(serializers.ModelSerializer):
    widget = DashboardWidgetSerializer(read_only=True)
    widget_id = serializers.PrimaryKeyRelatedField(
        queryset=DashboardWidget.objects.all(),
        source='widget',
        write_only=True
    )
    
    class Meta:
        model = DashboardWidgetPlacement
        fields = ['id', 'widget', 'widget_id', 'position_x', 'position_y', 'width', 'height']


class DashboardLayoutSerializer(serializers.ModelSerializer):
    widgets = DashboardWidgetPlacementSerializer(
        source='dashboardwidgetplacement_set',
        many=True,
        read_only=True
    )
    
    class Meta:
        model = DashboardLayout
        fields = ['id', 'name', 'description', 'widgets', 'is_default', 'created_by', 'created_at', 'updated_at']


class UserDashboardPreferenceSerializer(serializers.ModelSerializer):
    layout = DashboardLayoutSerializer(read_only=True)
    layout_id = serializers.PrimaryKeyRelatedField(
        queryset=DashboardLayout.objects.all(),
        source='layout',
        write_only=True
    )
    
    class Meta:
        model = UserDashboardPreference
        fields = ['id', 'user', 'layout', 'layout_id', 'custom_settings']


# Serializers for aggregated data from different services

class LoanApplicationMetricsSerializer(serializers.Serializer):
    total_applications = serializers.IntegerField()
    applications_by_status = serializers.DictField(child=serializers.IntegerField())
    applications_by_product = serializers.DictField(child=serializers.IntegerField())
    average_processing_time = serializers.FloatField()
    total_loan_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    
    
class DocumentMetricsSerializer(serializers.Serializer):
    total_documents = serializers.IntegerField()
    documents_by_type = serializers.DictField(child=serializers.IntegerField())
    documents_by_status = serializers.DictField(child=serializers.IntegerField())
    documents_pending_approval = serializers.IntegerField()
    documents_pending_signature = serializers.IntegerField()
    
    
class BorrowerMetricsSerializer(serializers.Serializer):
    total_borrowers = serializers.IntegerField()
    active_borrowers = serializers.IntegerField()
    borrowers_by_state = serializers.DictField(child=serializers.IntegerField())
    new_borrowers_last_30_days = serializers.IntegerField()
    
    
class BrokerMetricsSerializer(serializers.Serializer):
    total_brokers = serializers.IntegerField()
    active_brokers = serializers.IntegerField()
    brokers_by_company = serializers.DictField(child=serializers.IntegerField())
    new_brokers_last_30_days = serializers.IntegerField()
    
    
class ProductMetricsSerializer(serializers.Serializer):
    total_products = serializers.IntegerField()
    active_products = serializers.IntegerField()
    products_by_usage = serializers.DictField(child=serializers.IntegerField())
    average_interest_rate = serializers.FloatField()
    
    
class DashboardOverviewSerializer(serializers.Serializer):
    loan_applications = LoanApplicationMetricsSerializer()
    documents = DocumentMetricsSerializer()
    borrowers = BorrowerMetricsSerializer()
    brokers = BrokerMetricsSerializer()
    products = ProductMetricsSerializer()
    last_updated = serializers.DateTimeField()
