from django.contrib import admin
from .models import (
    DashboardMetric,
    DashboardWidget,
    DashboardLayout,
    DashboardWidgetPlacement,
    UserDashboardPreference
)


@admin.register(DashboardMetric)
class DashboardMetricAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'name', 'category', 'metric_type', 'value', 'last_updated', 'is_active')
    list_filter = ('category', 'metric_type', 'is_active')
    search_fields = ('name', 'display_name', 'description')
    readonly_fields = ('last_updated',)


class DashboardWidgetPlacementInline(admin.TabularInline):
    model = DashboardWidgetPlacement
    extra = 1


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'name', 'widget_type', 'created_by', 'created_at', 'is_active')
    list_filter = ('widget_type', 'is_active')
    search_fields = ('name', 'display_name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('metrics',)


@admin.register(DashboardLayout)
class DashboardLayoutAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_default', 'created_by', 'created_at')
    list_filter = ('is_default',)
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [DashboardWidgetPlacementInline]


@admin.register(UserDashboardPreference)
class UserDashboardPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'layout')
    list_filter = ('layout',)
    search_fields = ('user__username', 'user__email')
