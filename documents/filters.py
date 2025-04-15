import django_filters
from django.db.models import Q
from .models import Document

class DocumentFilter(django_filters.FilterSet):
    """Advanced filter for documents"""
    title = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    keywords = django_filters.CharFilter(lookup_expr='icontains')
    tag = django_filters.CharFilter(field_name='tags__name', lookup_expr='iexact')
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    updated_after = django_filters.DateFilter(field_name='updated_at', lookup_expr='gte')
    updated_before = django_filters.DateFilter(field_name='updated_at', lookup_expr='lte')
    expires_after = django_filters.DateFilter(field_name='expiration_date', lookup_expr='gte')
    expires_before = django_filters.DateFilter(field_name='expiration_date', lookup_expr='lte')
    latest_version = django_filters.BooleanFilter(field_name='is_latest_version')
    search = django_filters.CharFilter(method='search_filter')
    
    class Meta:
        model = Document
        fields = {
            'application': ['exact'],
            'document_type': ['exact'],
            'category': ['exact'],
            'status': ['exact'],
            'version': ['exact', 'gt', 'lt'],
            'uploaded_by': ['exact'],
            'is_confidential': ['exact'],
            'access_level': ['exact', 'lte', 'gte'],
        }
    
    def search_filter(self, queryset, name, value):
        """Full text search across multiple fields"""
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(keywords__icontains=value) |
            Q(tags__name__icontains=value) |
            Q(version_notes__icontains=value)
        ).distinct()
