from rest_framework import serializers
from taggit.models import Tag
from taggit.serializers import (TagListSerializerField, TaggitSerializer)
from django.utils import timezone
from datetime import datetime

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
    shared_with_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        source='shared_with',
        write_only=True,
        required=False
    )
    
    class Meta:
        model = DocumentCollection
        fields = ['id', 'name', 'description', 'created_by', 'created_at', 'updated_at',
                  'is_shared', 'shared_with', 'shared_with_ids', 'parent', 'parent_name', 'full_path',
                  'icon', 'color', 'document_count']
    
    def get_parent_name(self, obj):
        return obj.parent.name if obj.parent else None
        
    def get_full_path(self, obj):
        return obj.get_full_path()
        
    def get_document_count(self, obj):
        return obj.get_document_count()
    
    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError("Name is required")
        if len(value) > 100:
            raise serializers.ValidationError("Name cannot be longer than 100 characters")
        return value
    
    def validate_parent(self, value):
        if value:
            try:
                DocumentCollection.objects.get(pk=value.id)
            except DocumentCollection.DoesNotExist:
                raise serializers.ValidationError("Parent collection does not exist")
        return value
    
    def validate(self, data):
        # Validate that parent is not the same as the collection itself (for updates)
        instance = getattr(self, 'instance', None)
        if instance and data.get('parent') and instance.id == data['parent'].id:
            raise serializers.ValidationError({"parent": "A collection cannot be its own parent"})
        
        # Check for circular parent relationships
        if data.get('parent') and instance:
            if self._would_create_circular_reference(instance, data['parent']):
                raise serializers.ValidationError({"parent": "This would create a circular reference"})
        
        return data
    
    def _would_create_circular_reference(self, collection, new_parent):
        """Check if setting new_parent as the parent of collection would create a circular reference"""
        current = new_parent
        while current:
            if current.id == collection.id:
                return True
            current = current.parent
        return False

class CustomMetadataFieldSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = CustomMetadataField
        fields = ['id', 'name', 'description', 'field_type', 'required', 
                  'default_value', 'options', 'document_types', 'created_by', 'created_at']
    
    def validate_name(self, value):
        if len(value) > 100:
            raise serializers.ValidationError("Name cannot be longer than 100 characters")
        return value
    
    def validate_field_type(self, value):
        valid_types = ['text', 'number', 'date', 'boolean', 'select', 'multi-select']
        if value not in valid_types:
            raise serializers.ValidationError(f"Field type must be one of: {', '.join(valid_types)}")
        return value
    
    def validate_options(self, value):
        if value and not isinstance(value, list):
            raise serializers.ValidationError("Options must be a list")
        return value
    
    def validate(self, data):
        # Validate that options are provided for select and multi-select fields
        if data.get('field_type') in ['select', 'multi-select'] and not data.get('options'):
            raise serializers.ValidationError({"options": "Options are required for select and multi-select fields"})
        return data

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
    
    def validate_value(self, value):
        if value == '':
            raise serializers.ValidationError("Value cannot be empty")
        return value
    
    def validate(self, data):
        field = data.get('field')
        value = data.get('value')
        
        if field and value:
            # Validate number fields
            if field.field_type == 'number':
                try:
                    float(value)
                except ValueError:
                    raise serializers.ValidationError({"value": "Value must be a number"})
                    
            # Validate date fields
            elif field.field_type == 'date':
                try:
                    datetime.strptime(value, '%Y-%m-%d')
                except ValueError:
                    raise serializers.ValidationError({"value": "Value must be a valid date in YYYY-MM-DD format"})
                    
            # Validate boolean fields
            elif field.field_type == 'boolean':
                if value.lower() not in ['true', 'false', '1', '0', 'yes', 'no']:
                    raise serializers.ValidationError({"value": "Value must be a boolean (true/false, 1/0, yes/no)"})
                    
            # Validate select fields
            elif field.field_type == 'select' and field.options:
                if value not in field.options:
                    raise serializers.ValidationError({"value": f"Value must be one of: {', '.join(field.options)}"})
                    
            # Validate multi-select fields
            elif field.field_type == 'multi-select' and field.options:
                try:
                    values = json.loads(value) if isinstance(value, str) else value
                    if not isinstance(values, list):
                        raise serializers.ValidationError({"value": "Value must be a list for multi-select fields"})
                    
                    for val in values:
                        if val not in field.options:
                            raise serializers.ValidationError({"value": f"All values must be from options: {', '.join(field.options)}"})
                except json.JSONDecodeError:
                    raise serializers.ValidationError({"value": "Value must be a valid JSON list for multi-select fields"})
                    
        return data

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
    
    def validate_source_document(self, value):
        try:
            Document.objects.get(pk=value.id)
        except Document.DoesNotExist:
            raise serializers.ValidationError("Source document does not exist")
        return value
    
    def validate_target_document(self, value):
        try:
            Document.objects.get(pk=value.id)
        except Document.DoesNotExist:
            raise serializers.ValidationError("Target document does not exist")
        return value
    
    def validate_relationship_type(self, value):
        valid_types = ['parent', 'child', 'related', 'supersedes', 'superseded_by', 'version', 'custom']
        if value not in valid_types:
            raise serializers.ValidationError(f"Relationship type must be one of: {', '.join(valid_types)}")
        return value
    
    def validate(self, data):
        # Validate that source and target documents are different
        if data.get('source_document') and data.get('target_document'):
            if data['source_document'].id == data['target_document'].id:
                raise serializers.ValidationError({"target_document": "Source and target documents cannot be the same"})
        
        # Validate that custom_type is provided when relationship_type is 'custom'
        if data.get('relationship_type') == 'custom' and not data.get('custom_type'):
            raise serializers.ValidationError({"custom_type": "Custom type is required when relationship type is 'custom'"})
        
        # Check for circular relationships
        if data.get('relationship_type') in ['parent', 'child']:
            source_doc = data.get('source_document')
            target_doc = data.get('target_document')
            
            if data.get('relationship_type') == 'parent':
                # Check if target is already a parent of source (directly or indirectly)
                if self._is_parent(target_doc, source_doc):
                    raise serializers.ValidationError({"target_document": "This would create a circular parent-child relationship"})
            else:  # child
                # Check if target is already a child of source (directly or indirectly)
                if self._is_parent(source_doc, target_doc):
                    raise serializers.ValidationError({"target_document": "This would create a circular parent-child relationship"})
        
        return data
    
    def _is_parent(self, potential_parent, document):
        """Check if potential_parent is already a parent of document (directly or indirectly)"""
        if not potential_parent or not document:
            return False
            
        # Check direct parent relationship
        parent_relationships = DocumentRelationship.objects.filter(
            source_document=document,
            target_document=potential_parent,
            relationship_type='parent'
        )
        if parent_relationships.exists():
            return True
            
        # Check indirect parent relationships (recursively)
        parent_relationships = DocumentRelationship.objects.filter(
            source_document=document,
            relationship_type='parent'
        )
        for rel in parent_relationships:
            if self._is_parent(potential_parent, rel.target_document):
                return True
                
        return False

class DocumentCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = DocumentComment
        fields = ['id', 'document', 'user', 'text', 'created_at', 'updated_at']

class DocumentApprovalSerializer(serializers.ModelSerializer):
    reviewer = UserSerializer(read_only=True)
    requested_by = UserSerializer(read_only=True)
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='reviewer',
        write_only=True,
        required=True
    )
    
    class Meta:
        model = DocumentApproval
        fields = ['id', 'document', 'reviewer', 'reviewer_id', 'requested_by', 'status', 'comments', 
                  'requested_date', 'response_date', 'approval_level']
    
    def validate_document(self, value):
        try:
            Document.objects.get(pk=value.id)
        except Document.DoesNotExist:
            raise serializers.ValidationError("Document does not exist")
        return value
    
    def validate_status(self, value):
        valid_statuses = ['pending', 'approved', 'rejected', 'cancelled']
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Status must be one of: {', '.join(valid_statuses)}")
        return value
    
    def validate_approval_level(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Approval level must be between 1 and 5")
        return value
    
    def validate(self, data):
        # Validate that comments are provided when status is 'rejected'
        if data.get('status') == 'rejected' and not data.get('comments'):
            raise serializers.ValidationError({"comments": "Comments are required when status is rejected"})
        return data

class DocumentSignatureRequestSerializer(serializers.ModelSerializer):
    signer = UserSerializer(read_only=True)
    requested_by = UserSerializer(read_only=True)
    signer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='signer',
        write_only=True,
        required=True
    )
    
    class Meta:
        model = DocumentSignatureRequest
        fields = ['id', 'document', 'signer', 'signer_id', 'requested_by', 'status', 'message', 
                  'requested_date', 'viewed_date', 'response_date', 'due_date', 'decline_reason']
    
    def validate_document(self, value):
        try:
            Document.objects.get(pk=value.id)
        except Document.DoesNotExist:
            raise serializers.ValidationError("Document does not exist")
        return value
    
    def validate_status(self, value):
        valid_statuses = ['pending', 'viewed', 'signed', 'declined', 'expired', 'cancelled']
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Status must be one of: {', '.join(valid_statuses)}")
        return value
    
    def validate_due_date(self, value):
        if value and value < timezone.now().date():
            raise serializers.ValidationError("Due date cannot be in the past")
        return value
    
    def validate(self, data):
        # Validate that decline_reason is provided when status is 'declined'
        if data.get('status') == 'declined' and not data.get('decline_reason'):
            raise serializers.ValidationError({"decline_reason": "Decline reason is required when status is declined"})
        return data

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
    
    def validate_title(self, value):
        if not value:
            raise serializers.ValidationError("Title is required")
        if len(value) > 255:
            raise serializers.ValidationError("Title cannot be longer than 255 characters")
        return value
    
    def validate_document_type(self, value):
        valid_types = ['contract', 'application', 'id', 'financial', 'legal', 'other']
        if value and value not in valid_types:
            raise serializers.ValidationError(f"Document type must be one of: {', '.join(valid_types)}")
        return value
    
    def validate_status(self, value):
        valid_statuses = ['draft', 'pending', 'approved', 'rejected', 'archived']
        if value and value not in valid_statuses:
            raise serializers.ValidationError(f"Status must be one of: {', '.join(valid_statuses)}")
        return value
    
    def validate_expiration_date(self, value):
        if value and value < timezone.now().date():
            raise serializers.ValidationError("Expiration date cannot be in the past")
        return value
    
    def validate_tags(self, value):
        if value and not isinstance(value, list):
            raise serializers.ValidationError("Tags must be a list")
        return value
