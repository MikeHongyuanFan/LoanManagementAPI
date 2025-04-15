from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BorrowerViewSet,
    borrower_list, borrower_detail, borrower_create, 
    borrower_edit, borrower_add_note, borrower_delete
)

# API router
router = DefaultRouter()
router.register(r'borrowers', BorrowerViewSet)

# URL patterns
urlpatterns = [
    # API endpoints
    path('', include(router.urls)),
    
    # HTML views
    path('borrowers/', borrower_list, name='borrower_list'),
    path('borrowers/<int:pk>/', borrower_detail, name='borrower_detail'),
    path('borrowers/create/', borrower_create, name='borrower_create'),
    path('borrowers/<int:pk>/edit/', borrower_edit, name='borrower_edit'),
    path('borrowers/<int:pk>/add-note/', borrower_add_note, name='borrower_add_note'),
    path('borrowers/<int:pk>/delete/', borrower_delete, name='borrower_delete'),
]
