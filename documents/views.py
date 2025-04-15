from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import (
    Document, DocumentCategory, DocumentTemplate, DocumentComment,
    DocumentApproval, DocumentSignatureRequest, DocumentSignature,
    DocumentCollection, DocumentRelationship, CustomMetadataField,
    DocumentMetadata
)
from .serializers import (
    DocumentSerializer, DocumentCategorySerializer, DocumentTemplateSerializer,
    DocumentCommentSerializer, DocumentApprovalSerializer,
    DocumentSignatureRequestSerializer, DocumentSignatureSerializer,
    DocumentCollectionSerializer, DocumentRelationshipSerializer,
    CustomMetadataFieldSerializer, DocumentMetadataSerializer
)
from notifications.services import create_signature_request_notification

class DocumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for documents
    """
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user, last_modified_by=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(last_modified_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def request_signature(self, request, pk=None):
        """Request signature for a document"""
        document = self.get_object()
        
        # Validate request data
        if 'signer_id' not in request.data:
            return Response({"signer_id": "This field is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create signature request
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            signer = User.objects.get(pk=request.data['signer_id'])
        except User.DoesNotExist:
            return Response({"signer_id": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if there's already a pending signature request
        existing_request = DocumentSignatureRequest.objects.filter(
            document=document,
            signer=signer,
            status='pending'
        ).first()
        
        if existing_request:
            return Response(
                {"detail": "There is already a pending signature request for this document and signer"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create signature request
        signature_request = DocumentSignatureRequest.objects.create(
            document=document,
            signer=signer,
            requested_by=request.user,
            status='pending',
            message=request.data.get('message', ''),
            requested_date=timezone.now(),
            due_date=request.data.get('due_date')
        )
        
        # Update document status
        document.status = 'pending_signature'
        document.save()
        
        # Create notification for the signer
        create_signature_request_notification(signature_request)
        
        return Response({
            "id": signature_request.id,
            "document": document.id,
            "signer": {
                "id": signer.id,
                "username": signer.username,
                "email": signer.email
            },
            "status": "pending",
            "requested_date": signature_request.requested_date,
            "due_date": signature_request.due_date
        }, status=status.HTTP_201_CREATED)
        
    @action(detail=True, methods=['post'])
    def add_relationship(self, request, pk=None):
        """Add a relationship from this document to another document"""
        source_document = self.get_object()
        
        # Validate request data
        if 'target_document_id' not in request.data:
            return Response({"target_document_id": "This field is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        if 'relationship_type' not in request.data:
            return Response({"relationship_type": "This field is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get target document
        try:
            target_document = Document.objects.get(pk=request.data['target_document_id'])
        except Document.DoesNotExist:
            return Response({"target_document_id": "Target document not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Validate relationship type
        relationship_type = request.data['relationship_type']
        valid_types = ['supersedes', 'supplements', 'references', 'requires', 'amends', 'custom']
        if relationship_type not in valid_types:
            return Response(
                {"relationship_type": f"Must be one of: {', '.join(valid_types)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # If custom type, require custom_type field
        if relationship_type == 'custom' and 'custom_type' not in request.data:
            return Response({"custom_type": "Required when relationship_type is 'custom'"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if relationship already exists
        existing_relationship = DocumentRelationship.objects.filter(
            source_document=source_document,
            target_document=target_document,
            relationship_type=relationship_type
        ).first()
        
        if existing_relationship:
            return Response(
                {"detail": "This relationship already exists between these documents"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create relationship
        relationship = DocumentRelationship.objects.create(
            source_document=source_document,
            target_document=target_document,
            relationship_type=relationship_type,
            custom_type=request.data.get('custom_type', ''),
            description=request.data.get('description', ''),
            created_by=request.user
        )
        
        return Response({
            "id": relationship.id,
            "source_document": source_document.id,
            "target_document": target_document.id,
            "relationship_type": relationship_type,
            "custom_type": relationship.custom_type,
            "description": relationship.description,
            "created_at": relationship.created_at
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def remove_relationship(self, request, pk=None):
        """Remove a relationship from this document to another document"""
        source_document = self.get_object()
        
        # Validate request data
        if 'relationship_id' not in request.data:
            return Response({"relationship_id": "This field is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get relationship
        try:
            relationship = DocumentRelationship.objects.get(
                pk=request.data['relationship_id'],
                source_document=source_document
            )
        except DocumentRelationship.DoesNotExist:
            return Response({"relationship_id": "Relationship not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if user has permission to delete
        if relationship.created_by != request.user and not request.user.is_staff:
            return Response(
                {"detail": "You do not have permission to delete this relationship"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Store relationship details for response
        response_data = {
            "id": relationship.id,
            "source_document": relationship.source_document.id,
            "target_document": relationship.target_document.id,
            "relationship_type": relationship.relationship_type,
            "deleted": True
        }
        
        # Delete relationship
        relationship.delete()
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def relationships(self, request, pk=None):
        """Get all relationships for this document (both source and target)"""
        document = self.get_object()
        
        # Get relationships where document is source
        source_relationships = DocumentRelationship.objects.filter(source_document=document)
        source_data = []
        for rel in source_relationships:
            source_data.append({
                "id": rel.id,
                "source_document": rel.source_document.id,
                "target_document": rel.target_document.id,
                "target_document_title": rel.target_document.title,
                "relationship_type": rel.relationship_type,
                "custom_type": rel.custom_type,
                "description": rel.description,
                "created_at": rel.created_at,
                "direction": "outgoing"
            })
        
        # Get relationships where document is target
        target_relationships = DocumentRelationship.objects.filter(target_document=document)
        target_data = []
        for rel in target_relationships:
            target_data.append({
                "id": rel.id,
                "source_document": rel.source_document.id,
                "source_document_title": rel.source_document.title,
                "target_document": rel.target_document.id,
                "relationship_type": rel.relationship_type,
                "custom_type": rel.custom_type,
                "description": rel.description,
                "created_at": rel.created_at,
                "direction": "incoming"
            })
        
        return Response({
            "outgoing_relationships": source_data,
            "incoming_relationships": target_data,
            "total_relationships": len(source_data) + len(target_data)
        }, status=status.HTTP_200_OK)

class DocumentCategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for document categories
    """
    queryset = DocumentCategory.objects.all()
    serializer_class = DocumentCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

class DocumentTemplateViewSet(viewsets.ModelViewSet):
    """
    API endpoint for document templates
    """
    queryset = DocumentTemplate.objects.all()
    serializer_class = DocumentTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class DocumentCommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for document comments
    """
    queryset = DocumentComment.objects.all()
    serializer_class = DocumentCommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class DocumentApprovalViewSet(viewsets.ModelViewSet):
    """
    API endpoint for document approvals
    """
    queryset = DocumentApproval.objects.all()
    serializer_class = DocumentApprovalSerializer
    permission_classes = [permissions.IsAuthenticated]

class DocumentSignatureRequestViewSet(viewsets.ModelViewSet):
    """
    API endpoint for document signature requests
    """
    queryset = DocumentSignatureRequest.objects.all()
    serializer_class = DocumentSignatureRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

class DocumentSignatureViewSet(viewsets.ModelViewSet):
    """
    API endpoint for document signatures
    """
    queryset = DocumentSignature.objects.all()
    serializer_class = DocumentSignatureSerializer
    permission_classes = [permissions.IsAuthenticated]

class DocumentCollectionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for document collections
    """
    queryset = DocumentCollection.objects.all()
    serializer_class = DocumentCollectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_document(self, request, pk=None):
        """Add a document to a collection"""
        collection = self.get_object()
        
        # Validate request data
        if 'document_id' not in request.data:
            return Response({"document_id": "This field is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            document = Document.objects.get(pk=request.data['document_id'])
        except Document.DoesNotExist:
            return Response({"document_id": "Document not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Add document to collection
        collection.documents.add(document)
        
        return Response({"detail": "Document added to collection"}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def remove_document(self, request, pk=None):
        """Remove a document from a collection"""
        collection = self.get_object()
        
        # Validate request data
        if 'document_id' not in request.data:
            return Response({"document_id": "This field is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            document = Document.objects.get(pk=request.data['document_id'])
        except Document.DoesNotExist:
            return Response({"document_id": "Document not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Remove document from collection
        collection.documents.remove(document)
        
        return Response({"detail": "Document removed from collection"}, status=status.HTTP_200_OK)

class DocumentRelationshipViewSet(viewsets.ModelViewSet):
    """
    API endpoint for document relationships
    """
    queryset = DocumentRelationship.objects.all()
    serializer_class = DocumentRelationshipSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
        
    @action(detail=False, methods=['post'])
    def add_relationship(self, request):
        """Add a relationship between two documents"""
        # Validate request data
        required_fields = ['source_document_id', 'target_document_id', 'relationship_type']
        for field in required_fields:
            if field not in request.data:
                return Response({field: "This field is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get documents
        try:
            source_document = Document.objects.get(pk=request.data['source_document_id'])
        except Document.DoesNotExist:
            return Response({"source_document_id": "Source document not found"}, status=status.HTTP_404_NOT_FOUND)
            
        try:
            target_document = Document.objects.get(pk=request.data['target_document_id'])
        except Document.DoesNotExist:
            return Response({"target_document_id": "Target document not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Validate relationship type
        relationship_type = request.data['relationship_type']
        valid_types = ['supersedes', 'supplements', 'references', 'requires', 'amends', 'custom']
        if relationship_type not in valid_types:
            return Response(
                {"relationship_type": f"Must be one of: {', '.join(valid_types)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # If custom type, require custom_type field
        if relationship_type == 'custom' and 'custom_type' not in request.data:
            return Response({"custom_type": "Required when relationship_type is 'custom'"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if relationship already exists
        existing_relationship = DocumentRelationship.objects.filter(
            source_document=source_document,
            target_document=target_document,
            relationship_type=relationship_type
        ).first()
        
        if existing_relationship:
            return Response(
                {"detail": "This relationship already exists between these documents"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create relationship
        relationship = DocumentRelationship.objects.create(
            source_document=source_document,
            target_document=target_document,
            relationship_type=relationship_type,
            custom_type=request.data.get('custom_type', ''),
            description=request.data.get('description', ''),
            created_by=request.user
        )
        
        return Response({
            "id": relationship.id,
            "source_document": source_document.id,
            "target_document": target_document.id,
            "relationship_type": relationship_type,
            "custom_type": relationship.custom_type,
            "description": relationship.description,
            "created_at": relationship.created_at
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'])
    def remove_relationship(self, request, pk=None):
        """Remove a relationship between documents"""
        relationship = self.get_object()
        
        # Check if user has permission to delete
        if relationship.created_by != request.user and not request.user.is_staff:
            return Response(
                {"detail": "You do not have permission to delete this relationship"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Store relationship details for response
        response_data = {
            "id": relationship.id,
            "source_document": relationship.source_document.id,
            "target_document": relationship.target_document.id,
            "relationship_type": relationship.relationship_type,
            "deleted": True
        }
        
        # Delete relationship
        relationship.delete()
        
        return Response(response_data, status=status.HTTP_200_OK)

class CustomMetadataFieldViewSet(viewsets.ModelViewSet):
    """
    API endpoint for custom metadata fields
    """
    queryset = CustomMetadataField.objects.all()
    serializer_class = CustomMetadataFieldSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class DocumentMetadataViewSet(viewsets.ModelViewSet):
    """
    API endpoint for document metadata
    """
    serializer_class = DocumentMetadataSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Optionally restricts the returned metadata to a given document,
        by filtering against a `document` query parameter in the URL.
        """
        queryset = DocumentMetadata.objects.all()
        document_id = self.request.query_params.get('document')
        if document_id is not None:
            queryset = queryset.filter(document__id=document_id)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
