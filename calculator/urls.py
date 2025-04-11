from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LoanCalculationViewSet, RepaymentScheduleViewSet,
    FeeViewSet, ApplicationFeeViewSet
)

router = DefaultRouter()
router.register(r'calculations', LoanCalculationViewSet)
router.register(r'repayments', RepaymentScheduleViewSet)
router.register(r'fees', FeeViewSet)
router.register(r'application-fees', ApplicationFeeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
