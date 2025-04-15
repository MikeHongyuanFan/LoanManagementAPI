from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views_endpoints import document_metadata_bulk_update, signature_request_respond
from .views_approval import (
    request_document_approval, respond_to_approval, 
    cancel_approval_request, reassign_approval
)
from .views_version import (
    create_document_version, get_document_versions,
    revert_to_version, compare_versions
)
from .views_search import (
    advanced_document_search, full_text_search,
    recent_documents, document_suggestions
)

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
    
    # Document metadata endpoints
    path('documents/<int:pk>/update-metadata/', document_metadata_bulk_update, name='document-metadata-bulk-update'),
    
    # Signature request endpoints
    path('signature-requests/<int:pk>/respond/', signature_request_respond, name='signature-request-respond'),
    
    # Document approval endpoints
    path('documents/<int:document_id>/request-approval/', request_document_approval, name='request-document-approval'),
    path('approvals/<int:approval_id>/respond/', respond_to_approval, name='respond-to-approval'),
    path('approvals/<int:approval_id>/cancel/', cancel_approval_request, name='cancel-approval-request'),
    path('approvals/<int:approval_id>/reassign/', reassign_approval, name='reassign-approval'),
    
    # Document version endpoints
    path('documents/<int:document_id>/create-version/', create_document_version, name='create-document-version'),
    path('documents/<int:document_id>/versions/', get_document_versions, name='get-document-versions'),
    path('documents/<int:document_id>/revert/<int:version_id>/', revert_to_version, name='revert-to-version'),
    path('versions/compare/<int:version1_id>/<int:version2_id>/', compare_versions, name='compare-versions'),
    
    # Document search endpoints
    path('search/', advanced_document_search, name='advanced-document-search'),
    path('search/full-text/', full_text_search, name='full-text-search'),
    path('documents/recent/', recent_documents, name='recent-documents'),
    path('documents/suggestions/', document_suggestions, name='document-suggestions'),
]
