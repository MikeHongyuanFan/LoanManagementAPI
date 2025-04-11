"""
Document management models
"""
import os
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator

def document_upload_path(instance, filename):
    """Generate upload path for document files
    
    Args:
        instance: Document instance
        filename: Original filename
    
    Returns:
        Upload path string
    """
    # Get the current date
    now = timezone.now()
    
    # Create path: documents/YYYY/MM/DD/document_type/filename
    path = f"documents/{now.year}/{now.month:02d}/{now.day:02d}/{instance.document_type}/"
    
    # Add user folder if available
    if instance.uploaded_by:
        path = os.path.join(path, f"user_{instance.uploaded_by.id}")
    
    # Return full path with filename
    return os.path.join(path, filename)

class DocumentCategory(models.Model):
    """Document category model"""
    name = models.CharField(max_length=100, null=True, blank=True, default="Uncategorized")
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    icon = models.CharField(max_length=50, blank=True, null=True, help_text="Icon class name (e.g., 'fa-file-pdf')")
    color = models.CharField(max_length=20, blank=True, null=True, help_text="Color code (e.g., '#FF5733')")
    is_system = models.BooleanField(default=False, help_text="System categories cannot be deleted")
    auto_categorize_rules = models.JSONField(null=True, blank=True, help_text="Rules for auto-categorization")
    
    class Meta:
        verbose_name_plural = "Document categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name or "Unnamed Category"
        
    def get_full_path(self):
        """Get the full category path (including parents)"""
        path = [self.name]
        parent = self.parent
        
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent
            
        return " / ".join(path)

class DocumentTemplate(models.Model):
    """Document template model"""
    name = models.CharField(max_length=100, null=True, blank=True, default="Untitled Template")
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='document_templates/', null=True, blank=True)
    template_type = models.CharField(max_length=50, choices=[
        ('html', 'HTML Template'),
        ('docx', 'Word Template'),
        ('pdf', 'PDF Form')
    ], default='html', null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name or "Unnamed Template"

class DocumentCollection(models.Model):
    """Document collection model for organizing documents into folders/collections"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_collections')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_shared = models.BooleanField(default=False, help_text="Whether this collection is shared with other users")
    shared_with = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='shared_collections')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcollections')
    icon = models.CharField(max_length=50, blank=True, null=True, help_text="Icon class name (e.g., 'fa-folder')")
    color = models.CharField(max_length=20, blank=True, null=True, help_text="Color code (e.g., '#4287f5')")
    
    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return self.name
        
    def get_full_path(self):
        """Get the full collection path (including parents)"""
        path = [self.name]
        parent = self.parent
        
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent
            
        return " / ".join(path)
        
    def get_document_count(self):
        """Get the total number of documents in this collection and subcollections"""
        count = self.documents.count()
        
        for subcollection in self.subcollections.all():
            count += subcollection.get_document_count()
            
        return count

class Document(models.Model):
    """Document model"""
    title = models.CharField(max_length=255, null=True, blank=True, default="Untitled Document")
    description = models.TextField(blank=True, null=True)
    file = models.FileField(
        upload_to=document_upload_path, 
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'jpg', 'jpeg', 'png'])],
        null=True,
        blank=True
    )
    document_type = models.CharField(max_length=50, choices=[
        ('application', 'Application Document'),
        ('agreement', 'Loan Agreement'),
        ('identification', 'Identification Document'),
        ('financial', 'Financial Document'),
        ('property', 'Property Document'),
        ('other', 'Other')
    ], default='other', null=True, blank=True)
    application = models.ForeignKey('applications.Application', on_delete=models.CASCADE, null=True, blank=True, related_name='documents')
    category = models.ForeignKey(DocumentCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    collections = models.ManyToManyField(DocumentCollection, blank=True, related_name='documents')
    tags = models.ManyToManyField('taggit.Tag', blank=True, related_name='documents')
    keywords = models.CharField(max_length=255, blank=True, null=True, help_text="Comma-separated keywords")
    status = models.CharField(max_length=50, choices=[
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('pending_signature', 'Pending Signature'),
        ('signature_declined', 'Signature Declined'),
        ('signed', 'Signed'),
        ('expired', 'Expired'),
        ('archived', 'Archived')
    ], default='draft', null=True, blank=True)
    access_level = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)],
                                      help_text="1: Public, 2: Internal, 3: Restricted, 4: Confidential, 5: Highly Confidential",
                                      null=True, blank=True)
    is_confidential = models.BooleanField(default=False)
    is_favorite = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    expiration_date = models.DateField(null=True, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_documents')
    last_modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='modified_documents')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Versioning fields
    parent_document = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='versions')
    version = models.IntegerField(default=1, null=True, blank=True)
    version_notes = models.TextField(blank=True, null=True)
    is_latest_version = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title or "Unnamed Document"
    
    def save(self, *args, **kwargs):
        # Set expiration date for certain document types if not provided
        if not self.expiration_date and self.document_type == 'identification':
            self.expiration_date = timezone.now().date() + timezone.timedelta(days=365)
        
        super().save(*args, **kwargs)
        
    def get_related_documents(self):
        """Get all documents related to this document"""
        source_relationships = self.related_to.all()
        target_relationships = self.related_from.all()
        
        related_docs = []
        
        for rel in source_relationships:
            related_docs.append({
                'document': rel.target_document,
                'relationship': rel.relationship_type,
                'custom_type': rel.custom_type,
                'direction': 'outgoing'
            })
            
        for rel in target_relationships:
            related_docs.append({
                'document': rel.source_document,
                'relationship': rel.relationship_type,
                'custom_type': rel.custom_type,
                'direction': 'incoming'
            })
            
        return related_docs

class DocumentComment(models.Model):
    """Document comment model"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        user_str = self.user.username if self.user else "Unknown User"
        doc_str = str(self.document) if self.document else "Unknown Document"
        return f"Comment by {user_str} on {doc_str}"

class DocumentApproval(models.Model):
    """Document approval model"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='approvals', null=True, blank=True)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='document_approvals', null=True, blank=True)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='requested_approvals',
        null=True,
        blank=True
    )
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')
    ], default='pending', null=True, blank=True)
    comments = models.TextField(blank=True, null=True)
    requested_date = models.DateTimeField(auto_now_add=True)
    response_date = models.DateTimeField(null=True, blank=True)
    approval_level = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)
    
    class Meta:
        ordering = ['requested_date']
    
    def __str__(self):
        reviewer_str = self.reviewer.username if self.reviewer else "Unknown Reviewer"
        doc_str = str(self.document) if self.document else "Unknown Document"
        return f"Approval by {reviewer_str} for {doc_str}"

class DocumentRelationship(models.Model):
    """Model to define relationships between documents"""
    source_document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='related_to')
    target_document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='related_from')
    relationship_type = models.CharField(max_length=50, choices=[
        ('supersedes', 'Supersedes'),
        ('supplements', 'Supplements'),
        ('references', 'References'),
        ('requires', 'Requires'),
        ('amends', 'Amends'),
        ('custom', 'Custom')
    ])
    custom_type = models.CharField(max_length=100, blank=True, null=True, help_text="Custom relationship type name")
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_relationships')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('source_document', 'target_document', 'relationship_type')
        
    def __str__(self):
        relationship = self.custom_type if self.relationship_type == 'custom' else self.relationship_type
        return f"{self.source_document} {relationship} {self.target_document}"

class CustomMetadataField(models.Model):
    """Model for defining custom metadata fields for documents"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    field_type = models.CharField(max_length=20, choices=[
        ('text', 'Text'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('boolean', 'Boolean'),
        ('select', 'Select')
    ])
    required = models.BooleanField(default=False)
    default_value = models.JSONField(null=True, blank=True)
    options = models.JSONField(null=True, blank=True, help_text="Options for select field type")
    document_types = models.JSONField(null=True, blank=True, help_text="Document types this field applies to")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_metadata_fields')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class DocumentMetadata(models.Model):
    """Model for storing custom metadata values for documents"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='custom_metadata')
    field = models.ForeignKey(CustomMetadataField, on_delete=models.CASCADE, related_name='values')
    value = models.JSONField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_metadata')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('document', 'field')
        
    def __str__(self):
        return f"{self.document} - {self.field}: {self.value}"

class DocumentSignatureRequest(models.Model):
    """Document signature request model"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='signature_requests', null=True, blank=True)
    signer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='signature_requests', null=True, blank=True)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='requested_signatures',
        null=True,
        blank=True
    )
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('viewed', 'Viewed'),
        ('signed', 'Signed'),
        ('declined', 'Declined'),
        ('cancelled', 'Cancelled')
    ], default='pending', null=True, blank=True)
    message = models.TextField(blank=True, null=True)
    requested_date = models.DateTimeField(auto_now_add=True)
    viewed_date = models.DateTimeField(null=True, blank=True)
    response_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    decline_reason = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['requested_date']
    
    def __str__(self):
        signer_str = self.signer.username if self.signer else "Unknown Signer"
        doc_str = str(self.document) if self.document else "Unknown Document"
        return f"Signature request for {signer_str} on {doc_str}"

class DocumentSignature(models.Model):
    """Document signature model"""
    signature_request = models.OneToOneField(
        DocumentSignatureRequest, 
        on_delete=models.CASCADE, 
        related_name='signature',
        null=True,
        blank=True
    )
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='signatures', null=True, blank=True)
    signer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='signatures', null=True, blank=True)
    signature_type = models.CharField(max_length=50, choices=[
        ('drawn', 'Drawn Signature'),
        ('typed', 'Typed Signature'),
        ('digital', 'Digital Signature')
    ], default='typed', null=True, blank=True)
    signature_data = models.TextField(blank=True, null=True)
    signature_date = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    verification_hash = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        signer_str = self.signer.username if self.signer else "Unknown Signer"
        doc_str = str(self.document) if self.document else "Unknown Document"
        return f"Signature by {signer_str} on {doc_str}"
