from rest_framework import serializers
from taggit.models import Tag
from taggit.serializers import (TagListSerializerField, TaggitSerializer)

# Custom implementation for TagListSerializerField to fix the set() issue
class CustomTagListSerializerField(serializers.ListField):
    child = serializers.CharField()

    def to_representation(self, value):
        return [tag.name for tag in value.all()]
        
    def to_internal_value(self, data):
        if not isinstance(data, list):
            raise serializers.ValidationError("Expected a list of tags")
        return data

# Custom implementation for TaggitSerializer
class CustomTaggitSerializer:
    """Mixin for handling tags in serializers"""
    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        instance = super().create(validated_data)
        
        if tags:
            instance.tags.set(*[tags])  # Pass as a single list argument
        
        return instance
    
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', [])
        instance = super().update(instance, validated_data)
        
        if tags:
            instance.tags.set(*[tags])  # Pass as a single list argument
        
        return instance

from .models import (
    Document, DocumentCategory, DocumentTemplate, DocumentComment, 
    DocumentApproval, DocumentSignatureRequest, DocumentSignature,
    DocumentCollection, DocumentRelationship, CustomMetadataField, DocumentMetadata
)
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class DocumentCategorySerializer(serializers.ModelSerializer):
    parent_name = serializers.SerializerMethodField()
    full_path = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentCategory
        fields = ['id', 'name', 'description', 'parent', 'parent_name', 'full_path', 
                  'icon', 'color', 'is_system', 'auto_categorize_rules']
    
    def get_parent_name(self, obj):
        return obj.parent.name if obj.parent else None
        
    def get_full_path(self, obj):
        return obj.get_full_path()

class DocumentTemplateSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = DocumentTemplate
        fields = ['id', 'name', 'description', 'file', 'template_type', 'created_by', 'created_at', 'updated_at']

class DocumentCollectionSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    shared_with = UserSerializer(many=True, read_only=True)
    parent_name = serializers.SerializerMethodField()
    full_path = serializers.SerializerMethodField()
    document_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentCollection
        fields = ['id', 'name', 'description', 'created_by', 'created_at', 'updated_at',
                  'is_shared', 'shared_with', 'parent', 'parent_name', 'full_path',
                  'icon', 'color', 'document_count']
    
    def get_parent_name(self, obj):
        return obj.parent.name if obj.parent else None
        
    def get_full_path(self, obj):
        return obj.get_full_path()
        
    def get_document_count(self, obj):
        return obj.get_document_count()

class CustomMetadataFieldSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = CustomMetadataField
        fields = ['id', 'name', 'description', 'field_type', 'required', 
                  'default_value', 'options', 'document_types', 'created_by', 'created_at']

class DocumentMetadataSerializer(serializers.ModelSerializer):
    field = CustomMetadataFieldSerializer(read_only=True)
    field_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomMetadataField.objects.all(),
        source='field',
        write_only=True
    )
    
    class Meta:
        model = DocumentMetadata
        fields = ['id', 'document', 'field', 'field_id', 'value', 'created_by', 'created_at', 'updated_at']

class DocumentRelationshipSerializer(serializers.ModelSerializer):
    source_document_title = serializers.SerializerMethodField()
    target_document_title = serializers.SerializerMethodField()
    created_by = UserSerializer(read_only=True)
    relationship_display = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentRelationship
        fields = ['id', 'source_document', 'source_document_title', 'target_document', 
                  'target_document_title', 'relationship_type', 'custom_type', 
                  'relationship_display', 'description', 'created_by', 'created_at']
    
    def get_source_document_title(self, obj):
        return obj.source_document.title
        
    def get_target_document_title(self, obj):
        return obj.target_document.title
        
    def get_relationship_display(self, obj):
        return obj.custom_type if obj.relationship_type == 'custom' else obj.get_relationship_type_display()

class DocumentCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = DocumentComment
        fields = ['id', 'document', 'user', 'text', 'created_at', 'updated_at']

class DocumentApprovalSerializer(serializers.ModelSerializer):
    reviewer = UserSerializer(read_only=True)
    requested_by = UserSerializer(read_only=True)
    
    class Meta:
        model = DocumentApproval
        fields = ['id', 'document', 'reviewer', 'requested_by', 'status', 'comments', 
                  'requested_date', 'response_date', 'approval_level']

class DocumentSignatureRequestSerializer(serializers.ModelSerializer):
    signer = UserSerializer(read_only=True)
    requested_by = UserSerializer(read_only=True)
    
    class Meta:
        model = DocumentSignatureRequest
        fields = ['id', 'document', 'signer', 'requested_by', 'status', 'message', 
                  'requested_date', 'viewed_date', 'response_date', 'due_date', 'decline_reason']

class DocumentSignatureSerializer(serializers.ModelSerializer):
    signer = UserSerializer(read_only=True)
    
    class Meta:
        model = DocumentSignature
        fields = ['id', 'signature_request', 'document', 'signer', 'signature_type', 
                  'signature_data', 'signature_date', 'ip_address', 'user_agent', 'verification_hash']

class DocumentSerializer(CustomTaggitSerializer, serializers.ModelSerializer):
    tags = CustomTagListSerializerField()
    category_name = serializers.SerializerMethodField()
    uploaded_by = UserSerializer(read_only=True)
    last_modified_by = UserSerializer(read_only=True)
    collections = DocumentCollectionSerializer(many=True, read_only=True)
    collection_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=DocumentCollection.objects.all(),
        source='collections',
        write_only=True,
        required=False
    )
    custom_metadata = DocumentMetadataSerializer(many=True, read_only=True)
    related_documents = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'description', 'file', 'document_type', 'application',
            'category', 'category_name', 'collections', 'collection_ids', 'tags', 'keywords',
            'status', 'access_level', 'is_confidential', 'is_favorite', 'is_pinned',
            'expiration_date', 'uploaded_by', 'last_modified_by', 'created_at', 'updated_at',
            'parent_document', 'version', 'version_notes', 'is_latest_version',
            'custom_metadata', 'related_documents'
        ]
    
    def get_category_name(self, obj):
        return obj.category.name if obj.category else None
        
    def get_related_documents(self, obj):
        related_docs = obj.get_related_documents()
        result = []
        
        for rel in related_docs:
            doc = rel['document']
            result.append({
                'id': doc.id,
                'title': doc.title,
                'document_type': doc.document_type,
                'relationship': rel['relationship'],
                'custom_type': rel['custom_type'],
                'direction': rel['direction']
            })
            
        return result
