from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'metrics', views.DashboardMetricViewSet)
router.register(r'widgets', views.DashboardWidgetViewSet)
router.register(r'layouts', views.DashboardLayoutViewSet)
router.register(r'preferences', views.UserDashboardPreferenceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('overview/', views.DashboardOverviewAPI.as_view(), name='dashboard-overview'),
    path('applications/', views.ApplicationDashboardAPI.as_view(), name='application-dashboard'),
    path('documents/', views.DocumentDashboardAPI.as_view(), name='document-dashboard'),
    path('entities/', views.BorrowerBrokerDashboardAPI.as_view(), name='entity-dashboard'),
]
