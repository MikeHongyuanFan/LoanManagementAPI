"""
URL Configuration for loan_management project
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers

from documents.views import (
    DocumentViewSet, DocumentCategoryViewSet, DocumentTemplateViewSet,
    DocumentCommentViewSet, DocumentApprovalViewSet,
    DocumentSignatureRequestViewSet, DocumentSignatureViewSet
)

# API router
router = routers.DefaultRouter()

# Document management routes
router.register(r'document-management/documents', DocumentViewSet, basename='document')
router.register(r'document-management/categories', DocumentCategoryViewSet, basename='document-category')
router.register(r'document-management/templates', DocumentTemplateViewSet, basename='document-template')
router.register(r'document-management/comments', DocumentCommentViewSet, basename='document-comment')
router.register(r'document-management/approvals', DocumentApprovalViewSet, basename='document-approval')
router.register(r'document-management/signature-requests', DocumentSignatureRequestViewSet, basename='signature-request')
router.register(r'document-management/signatures', DocumentSignatureViewSet, basename='signature')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('api/document-management/', include('documents.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
