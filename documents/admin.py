"""
Document admin configuration
"""
from django.contrib import admin
from .models import (
    Document, DocumentCategory, DocumentTemplate, 
    DocumentComment, DocumentApproval, DocumentSignatureRequest,
    DocumentSignature, DocumentCollection, DocumentRelationship,
    CustomMetadataField, DocumentMetadata
)

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin configuration for Document model"""
    list_display = ('title', 'document_type', 'status', 'uploaded_by', 'created_at', 'version')
    list_filter = ('document_type', 'status', 'access_level', 'is_confidential', 'is_favorite', 'is_pinned')
    search_fields = ('title', 'description', 'keywords')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'document_type', 'file')
        }),
        ('Metadata', {
            'fields': ('category', 'collections', 'tags', 'keywords', 'application')
        }),
        ('Status & Access', {
            'fields': ('status', 'access_level', 'is_confidential', 'is_favorite', 'is_pinned', 'expiration_date')
        }),
        ('Versioning', {
            'fields': ('parent_document', 'version', 'version_notes', 'is_latest_version')
        }),
        ('Audit', {
            'fields': ('uploaded_by', 'last_modified_by', 'created_at', 'updated_at')
        }),
    )

@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    """Admin configuration for DocumentCategory model"""
    list_display = ('name', 'parent', 'description', 'is_system')
    list_filter = ('is_system',)
    search_fields = ('name', 'description')

@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    """Admin configuration for DocumentTemplate model"""
    list_display = ('name', 'template_type', 'created_by', 'created_at')
    list_filter = ('template_type',)
    search_fields = ('name', 'description')

@admin.register(DocumentComment)
class DocumentCommentAdmin(admin.ModelAdmin):
    """Admin configuration for DocumentComment model"""
    list_display = ('document', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('text',)

@admin.register(DocumentApproval)
class DocumentApprovalAdmin(admin.ModelAdmin):
    """Admin configuration for DocumentApproval model"""
    list_display = ('document', 'reviewer', 'status', 'response_date')
    list_filter = ('status', 'approval_level')
    search_fields = ('comments',)

@admin.register(DocumentSignatureRequest)
class DocumentSignatureRequestAdmin(admin.ModelAdmin):
    """Admin configuration for DocumentSignatureRequest model"""
    list_display = ('document', 'signer', 'status', 'requested_date', 'response_date')
    list_filter = ('status',)
    search_fields = ('message', 'decline_reason')
    readonly_fields = ('requested_date', 'viewed_date', 'response_date')

@admin.register(DocumentSignature)
class DocumentSignatureAdmin(admin.ModelAdmin):
    """Admin configuration for DocumentSignature model"""
    list_display = ('document', 'signer', 'signature_type', 'signature_date')
    list_filter = ('signature_type',)
    readonly_fields = ('signature_date', 'ip_address', 'user_agent')

@admin.register(DocumentCollection)
class DocumentCollectionAdmin(admin.ModelAdmin):
    """Admin configuration for DocumentCollection model"""
    list_display = ('name', 'created_by', 'parent', 'is_shared', 'created_at')
    list_filter = ('is_shared',)
    search_fields = ('name', 'description')
    filter_horizontal = ('shared_with',)

@admin.register(DocumentRelationship)
class DocumentRelationshipAdmin(admin.ModelAdmin):
    """Admin configuration for DocumentRelationship model"""
    list_display = ('source_document', 'relationship_type', 'target_document', 'created_by')
    list_filter = ('relationship_type',)
    search_fields = ('description', 'custom_type')

@admin.register(CustomMetadataField)
class CustomMetadataFieldAdmin(admin.ModelAdmin):
    """Admin configuration for CustomMetadataField model"""
    list_display = ('name', 'field_type', 'required', 'created_by')
    list_filter = ('field_type', 'required')
    search_fields = ('name', 'description')

@admin.register(DocumentMetadata)
class DocumentMetadataAdmin(admin.ModelAdmin):
    """Admin configuration for DocumentMetadata model"""
    list_display = ('document', 'field', 'created_by', 'created_at')
    list_filter = ('field',)
    search_fields = ('value',)
