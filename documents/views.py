from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from .models import (
    Document, DocumentCategory, DocumentTemplate, DocumentComment, 
    DocumentApproval, DocumentSignatureRequest, DocumentSignature,
    DocumentCollection, DocumentRelationship, CustomMetadataField, DocumentMetadata
)
from .serializers import (
    DocumentSerializer, DocumentCategorySerializer, DocumentTemplateSerializer,
    DocumentCommentSerializer, DocumentApprovalSerializer, DocumentSignatureRequestSerializer,
    DocumentSignatureSerializer, DocumentCollectionSerializer, DocumentRelationshipSerializer,
    CustomMetadataFieldSerializer, DocumentMetadataSerializer
)
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Q
import json
import hashlib
import time

User = get_user_model()

class DocumentCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for document categories"""
    queryset = DocumentCategory.objects.all()
    serializer_class = DocumentCategorySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['parent', 'is_system']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'id']
    
    @action(detail=True, methods=['get'])
    def subcategories(self, request, pk=None):
        """Get all subcategories of a category"""
        category = self.get_object()
        subcategories = DocumentCategory.objects.filter(parent=category)
        serializer = self.get_serializer(subcategories, many=True)
        return Response(serializer.data)

class DocumentTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for document templates"""
    queryset = DocumentTemplate.objects.all()
    serializer_class = DocumentTemplateSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['template_type', 'created_by']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']

class DocumentCollectionViewSet(viewsets.ModelViewSet):
    """ViewSet for document collections"""
    queryset = DocumentCollection.objects.all()
    serializer_class = DocumentCollectionSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['created_by', 'is_shared', 'parent']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    
    def get_queryset(self):
        """Filter collections based on user"""
        user = self.request.user
        if user.is_authenticated:
            return DocumentCollection.objects.filter(
                Q(created_by=user) | Q(is_shared=True) | Q(shared_with=user)
            ).distinct()
        return DocumentCollection.objects.filter(is_shared=True)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def subcollections(self, request, pk=None):
        """Get all subcollections of a collection"""
        collection = self.get_object()
        subcollections = DocumentCollection.objects.filter(parent=collection)
        serializer = self.get_serializer(subcollections, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """Get all documents in a collection"""
        collection = self.get_object()
        documents = collection.documents.all()
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """Share a collection with users"""
        collection = self.get_object()
        user_ids = request.data.get('user_ids', [])
        
        if not user_ids:
            return Response({"error": "No user IDs provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        collection.is_shared = True
        collection.save()
        
        for user_id in user_ids:
            try:
                user = User.objects.get(id=user_id)
                collection.shared_with.add(user)
            except User.DoesNotExist:
                pass
        
        serializer = self.get_serializer(collection)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def unshare(self, request, pk=None):
        """Unshare a collection with users"""
        collection = self.get_object()
        user_ids = request.data.get('user_ids', [])
        
        if not user_ids:
            # Unshare with everyone
            collection.is_shared = False
            collection.shared_with.clear()
        else:
            # Unshare with specific users
            for user_id in user_ids:
                try:
                    user = User.objects.get(id=user_id)
                    collection.shared_with.remove(user)
                except User.DoesNotExist:
                    pass
            
            # If no more shared users, set is_shared to False
            if collection.shared_with.count() == 0:
                collection.is_shared = False
        
        collection.save()
        serializer = self.get_serializer(collection)
        return Response(serializer.data)

class CustomMetadataFieldViewSet(viewsets.ModelViewSet):
    """ViewSet for custom metadata fields"""
    queryset = CustomMetadataField.objects.all()
    serializer_class = CustomMetadataFieldSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['field_type', 'required', 'created_by']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def for_document_type(self, request):
        """Get metadata fields for a specific document type"""
        document_type = request.query_params.get('document_type')
        
        if not document_type:
            return Response({"error": "document_type parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        fields = CustomMetadataField.objects.filter(
            Q(document_types__isnull=True) | 
            Q(document_types__contains=[document_type])
        )
        
        serializer = self.get_serializer(fields, many=True)
        return Response(serializer.data)

class DocumentMetadataViewSet(viewsets.ModelViewSet):
    """ViewSet for document metadata"""
    queryset = DocumentMetadata.objects.all()
    serializer_class = DocumentMetadataSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['document', 'field']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class DocumentRelationshipViewSet(viewsets.ModelViewSet):
    """ViewSet for document relationships"""
    queryset = DocumentRelationship.objects.all()
    serializer_class = DocumentRelationshipSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['source_document', 'target_document', 'relationship_type', 'created_by']
    search_fields = ['description', 'custom_type']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for documents"""
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['document_type', 'category', 'status', 'application', 'is_confidential', 'is_favorite', 'is_pinned']
    search_fields = ['title', 'description', 'keywords']
    ordering_fields = ['title', 'created_at', 'updated_at', 'status']
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(last_modified_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_to_collection(self, request, pk=None):
        """Add document to a collection"""
        document = self.get_object()
        collection_id = request.data.get('collection_id')
        
        if not collection_id:
            return Response({"error": "collection_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            collection = DocumentCollection.objects.get(id=collection_id)
            document.collections.add(collection)
            return Response({"status": "Document added to collection"})
        except DocumentCollection.DoesNotExist:
            return Response({"error": "Collection not found"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def remove_from_collection(self, request, pk=None):
        """Remove document from a collection"""
        document = self.get_object()
        collection_id = request.data.get('collection_id')
        
        if not collection_id:
            return Response({"error": "collection_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            collection = DocumentCollection.objects.get(id=collection_id)
            document.collections.remove(collection)
            return Response({"status": "Document removed from collection"})
        except DocumentCollection.DoesNotExist:
            return Response({"error": "Collection not found"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        """Toggle favorite status of a document"""
        document = self.get_object()
        document.is_favorite = not document.is_favorite
        document.save()
        return Response({"is_favorite": document.is_favorite})
    
    @action(detail=True, methods=['post'])
    def toggle_pinned(self, request, pk=None):
        """Toggle pinned status of a document"""
        document = self.get_object()
        document.is_pinned = not document.is_pinned
        document.save()
        return Response({"is_pinned": document.is_pinned})
    
    @action(detail=True, methods=['post'])
    def add_metadata(self, request, pk=None):
        """Add custom metadata to a document"""
        document = self.get_object()
        field_id = request.data.get('field_id')
        value = request.data.get('value')
        
        if not field_id or value is None:
            return Response({"error": "field_id and value are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            field = CustomMetadataField.objects.get(id=field_id)
            
            # Check if metadata already exists for this field
            metadata, created = DocumentMetadata.objects.update_or_create(
                document=document,
                field=field,
                defaults={
                    'value': value,
                    'created_by': request.user
                }
            )
            
            serializer = DocumentMetadataSerializer(metadata)
            return Response(serializer.data)
        except CustomMetadataField.DoesNotExist:
            return Response({"error": "Metadata field not found"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def add_relationship(self, request, pk=None):
        """Add a relationship to another document"""
        source_document = self.get_object()
        target_document_id = request.data.get('target_document_id')
        relationship_type = request.data.get('relationship_type')
        custom_type = request.data.get('custom_type')
        description = request.data.get('description')
        
        if not target_document_id or not relationship_type:
            return Response({"error": "target_document_id and relationship_type are required"}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        if relationship_type == 'custom' and not custom_type:
            return Response({"error": "custom_type is required for custom relationship_type"}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        try:
            target_document = Document.objects.get(id=target_document_id)
            
            # Check if relationship already exists
            relationship, created = DocumentRelationship.objects.get_or_create(
                source_document=source_document,
                target_document=target_document,
                relationship_type=relationship_type,
                defaults={
                    'custom_type': custom_type,
                    'description': description,
                    'created_by': request.user
                }
            )
            
            if not created:
                return Response({"error": "Relationship already exists"}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = DocumentRelationshipSerializer(relationship)
            return Response(serializer.data)
        except Document.DoesNotExist:
            return Response({"error": "Target document not found"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def relationships(self, request, pk=None):
        """Get all relationships for a document"""
        document = self.get_object()
        related_docs = document.get_related_documents()
        
        return Response(related_docs)

class DocumentCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for document comments"""
    queryset = DocumentComment.objects.all()
    serializer_class = DocumentCommentSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['document', 'user']
    ordering_fields = ['created_at']
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class DocumentApprovalViewSet(viewsets.ModelViewSet):
    """ViewSet for document approvals"""
    queryset = DocumentApproval.objects.all()
    serializer_class = DocumentApprovalSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['document', 'reviewer', 'status', 'requested_by']
    ordering_fields = ['requested_date']
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a document"""
        approval = self.get_object()
        comments = request.data.get('comments', '')
        
        if approval.status != 'pending':
            return Response({"error": "This approval is not pending"}, status=status.HTTP_400_BAD_REQUEST)
        
        approval.status = 'approved'
        approval.comments = comments
        approval.response_date = timezone.now()
        approval.save()
        
        # Update document status if all approvals are complete
        document = approval.document
        pending_approvals = document.approvals.filter(status='pending').count()
        
        if pending_approvals == 0:
            document.status = 'approved'
            document.save()
        
        serializer = self.get_serializer(approval)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a document"""
        approval = self.get_object()
        comments = request.data.get('comments', '')
        
        if approval.status != 'pending':
            return Response({"error": "This approval is not pending"}, status=status.HTTP_400_BAD_REQUEST)
        
        approval.status = 'rejected'
        approval.comments = comments
        approval.response_date = timezone.now()
        approval.save()
        
        # Update document status
        document = approval.document
        document.status = 'rejected'
        document.save()
        
        serializer = self.get_serializer(approval)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reassign(self, request, pk=None):
        """Reassign approval to another reviewer"""
        approval = self.get_object()
        new_reviewer_id = request.data.get('reviewer_id')
        
        if not new_reviewer_id:
            return Response({"error": "reviewer_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if approval.status != 'pending':
            return Response({"error": "Only pending approvals can be reassigned"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            new_reviewer = User.objects.get(id=new_reviewer_id)
            approval.reviewer = new_reviewer
            approval.save()
            
            serializer = self.get_serializer(approval)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"error": "Reviewer not found"}, status=status.HTTP_404_NOT_FOUND)

class DocumentSignatureRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for document signature requests"""
    queryset = DocumentSignatureRequest.objects.all()
    serializer_class = DocumentSignatureRequestSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['document', 'signer', 'status', 'requested_by']
    ordering_fields = ['requested_date', 'due_date']
    
    @action(detail=True, methods=['post'])
    def sign(self, request, pk=None):
        """Sign a document"""
        signature_request = self.get_object()
        signature_type = request.data.get('signature_type', 'typed')
        signature_data = request.data.get('signature_data', '')
        
        if signature_request.status not in ['pending', 'viewed']:
            return Response({"error": "This signature request cannot be signed"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not signature_data:
            return Response({"error": "signature_data is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create signature
        signature = DocumentSignature.objects.create(
            signature_request=signature_request,
            document=signature_request.document,
            signer=signature_request.signer,
            signature_type=signature_type,
            signature_data=signature_data,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            verification_hash=self.generate_verification_hash(signature_request, signature_data)
        )
        
        # Update signature request status
        signature_request.status = 'signed'
        signature_request.response_date = timezone.now()
        signature_request.save()
        
        # Update document status
        document = signature_request.document
        pending_signatures = document.signature_requests.filter(status__in=['pending', 'viewed']).count()
        
        if pending_signatures == 0:
            document.status = 'signed'
            document.save()
        
        serializer = DocumentSignatureSerializer(signature)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        """Decline to sign a document"""
        signature_request = self.get_object()
        decline_reason = request.data.get('reason', '')
        
        if signature_request.status not in ['pending', 'viewed']:
            return Response({"error": "This signature request cannot be declined"}, status=status.HTTP_400_BAD_REQUEST)
        
        signature_request.status = 'declined'
        signature_request.decline_reason = decline_reason
        signature_request.response_date = timezone.now()
        signature_request.save()
        
        # Update document status
        document = signature_request.document
        document.status = 'signature_declined'
        document.save()
        
        serializer = self.get_serializer(signature_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a signature request"""
        signature_request = self.get_object()
        
        if signature_request.status not in ['pending', 'viewed']:
            return Response({"error": "This signature request cannot be cancelled"}, status=status.HTTP_400_BAD_REQUEST)
        
        signature_request.status = 'cancelled'
        signature_request.response_date = timezone.now()
        signature_request.save()
        
        serializer = self.get_serializer(signature_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_as_viewed(self, request, pk=None):
        """Mark a signature request as viewed"""
        signature_request = self.get_object()
        
        if signature_request.status != 'pending':
            return Response({"error": "Only pending signature requests can be marked as viewed"}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        signature_request.status = 'viewed'
        signature_request.viewed_date = timezone.now()
        signature_request.save()
        
        serializer = self.get_serializer(signature_request)
        return Response(serializer.data)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def generate_verification_hash(self, signature_request, signature_data):
        """Generate a verification hash for the signature"""
        # Create a unique hash based on document, signer, timestamp, and signature data
        data = f"{signature_request.document.id}:{signature_request.signer.id}:{time.time()}:{signature_data}"
        return hashlib.sha256(data.encode()).hexdigest()

class DocumentSignatureViewSet(viewsets.ModelViewSet):
    """ViewSet for document signatures"""
    queryset = DocumentSignature.objects.all()
    serializer_class = DocumentSignatureSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['document', 'signer', 'signature_type']
    ordering_fields = ['signature_date']
    
    @action(detail=True, methods=['get'])
    def verify(self, request, pk=None):
        """Verify a signature"""
        signature = self.get_object()
        
        verification_data = {
            'signature_id': signature.id,
            'document_id': signature.document.id,
            'document_title': signature.document.title,
            'signer': {
                'id': signature.signer.id,
                'name': f"{signature.signer.first_name} {signature.signer.last_name}",
                'email': signature.signer.email
            },
            'signature_type': signature.signature_type,
            'signature_date': signature.signature_date,
            'ip_address': signature.ip_address,
            'user_agent': signature.user_agent,
            'is_valid': True,  # In a real system, you would verify the hash here
            'verification_hash': signature.verification_hash
        }
        
        return Response(verification_data)
