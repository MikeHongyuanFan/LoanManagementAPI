from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import views_approval
from . import views_endpoints

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
router.register(r'metadata', views.DocumentMetadataViewSet, basename='document-metadata')

urlpatterns = [
    path('', include(router.urls)),
    
    # Document approval endpoints
    path('documents/<int:document_id>/request-approval/', views_approval.request_document_approval, name='request-document-approval'),
    path('approvals/<int:approval_id>/respond/', views_approval.respond_to_approval, name='respond-to-approval'),
    path('approvals/<int:approval_id>/cancel/', views_approval.cancel_approval_request, name='cancel-approval-request'),
    path('approvals/<int:approval_id>/reassign/', views_approval.reassign_approval, name='reassign-approval'),
    
    # Document metadata endpoints
    path('documents/<int:pk>/metadata/', views_endpoints.document_metadata_bulk_update, name='document-metadata-bulk-update'),
    
    # Signature endpoints
    path('signature-requests/<int:pk>/respond/', views_endpoints.signature_request_respond, name='signature-request-respond'),
    
    # Document relationship endpoints
    path('documents/<int:pk>/add-relationship/', views.DocumentViewSet.as_view({'post': 'add_relationship'}), name='document-add-relationship'),
    path('documents/<int:pk>/remove-relationship/', views.DocumentViewSet.as_view({'post': 'remove_relationship'}), name='document-remove-relationship'),
    path('documents/<int:pk>/relationships/', views.DocumentViewSet.as_view({'get': 'relationships'}), name='document-relationships'),
    path('relationships/add/', views.DocumentRelationshipViewSet.as_view({'post': 'add_relationship'}), name='add-relationship'),
    path('relationships/<int:pk>/remove/', views.DocumentRelationshipViewSet.as_view({'delete': 'remove_relationship'}), name='remove-relationship'),
]
