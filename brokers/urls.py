from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BrokerViewSet

router = DefaultRouter()
router.register(r'brokers', BrokerViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
