from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, FeeViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
    path('products/<int:product_id>/fees/', FeeViewSet.as_view({'get': 'list', 'post': 'create'}), name='product-fees'),
    path('products/<int:product_id>/fees/<int:pk>/', FeeViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='product-fee-detail'),
]
