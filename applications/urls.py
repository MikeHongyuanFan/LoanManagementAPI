from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ApplicationViewSet, ValuerViewSet, QSViewSet, ReferralViewSet,
    FeeViewSet, RepaymentViewSet, LoanExtensionViewSet
)

router = DefaultRouter()
router.register(r'applications', ApplicationViewSet)
router.register(r'valuers', ValuerViewSet)
router.register(r'qs', QSViewSet)
router.register(r'referrals', ReferralViewSet)
router.register(r'fees', FeeViewSet)
router.register(r'repayments', RepaymentViewSet)
router.register(r'loan-extensions', LoanExtensionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
