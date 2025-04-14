from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LoanCalculationViewSet, RepaymentScheduleViewSet,
    FeeViewSet, ApplicationFeeViewSet,
    MonthlyPaymentView, AmortizationScheduleView,
    LoanSummaryView, ProductPaymentView,
    CompareProductsView, AffordabilityView
)

router = DefaultRouter()
router.register(r'calculations', LoanCalculationViewSet)
router.register(r'repayments', RepaymentScheduleViewSet)
router.register(r'fees', FeeViewSet)
router.register(r'application-fees', ApplicationFeeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('monthly-payment/', MonthlyPaymentView.as_view(), name='monthly-payment'),
    path('amortization-schedule/', AmortizationScheduleView.as_view(), name='amortization-schedule'),
    path('loan-summary/', LoanSummaryView.as_view(), name='loan-summary'),
    path('product-payment/', ProductPaymentView.as_view(), name='product-payment'),
    path('compare-products/', CompareProductsView.as_view(), name='compare-products'),
    path('affordability/', AffordabilityView.as_view(), name='affordability'),
]
