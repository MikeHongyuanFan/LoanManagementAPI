from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'documents', views.DocumentViewSet)
router.register(r'categories', views.DocumentCategoryViewSet)
router.register(r'templates', views.DocumentTemplateViewSet)
router.register(r'comments', views.DocumentCommentViewSet)
router.register(r'approvals', views.DocumentApprovalViewSet)
router.register(r'signature-requests', views.DocumentSignatureRequestViewSet)
router.register(r'signatures', views.DocumentSignatureViewSet)
router.register(r'collections', views.DocumentCollectionViewSet)
router.register(r'relationships', views.DocumentRelationshipViewSet)
router.register(r'metadata-fields', views.CustomMetadataFieldViewSet)
router.register(r'document-metadata', views.DocumentMetadataViewSet, basename='document-metadata')

urlpatterns = [
    path('', include(router.urls)),
    # Add custom endpoint for document metadata bulk update
    path('documents/<int:pk>/update-metadata/', views.document_metadata_bulk_update, name='document-metadata-bulk-update'),
    # Add custom endpoint for signature request response
    path('signature-requests/<int:pk>/respond/', views.signature_request_respond, name='signature-request-respond'),
]
