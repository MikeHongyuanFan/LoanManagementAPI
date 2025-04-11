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


class DocumentRelationship(models.Model):
    """Model to define relationships between documents"""
    source_document = models.ForeignKey('Document', on_delete=models.CASCADE, related_name='related_to')
    target_document = models.ForeignKey('Document', on_delete=models.CASCADE, related_name='related_from')
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
    document = models.ForeignKey('Document', on_delete=models.CASCADE, related_name='custom_metadata')
    field = models.ForeignKey(CustomMetadataField, on_delete=models.CASCADE, related_name='values')
    value = models.JSONField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_metadata')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('document', 'field')
        
    def __str__(self):
        return f"{self.document} - {self.field}: {self.value}"
