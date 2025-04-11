"""
Document search indexes for Haystack
"""
import os
import textract
from django.conf import settings
from haystack import indexes
from .models import Document

class DocumentIndex(indexes.SearchIndex, indexes.Indexable):
    """Search index for Document model"""
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    description = indexes.CharField(model_attr='description', null=True)
    document_type = indexes.CharField(model_attr='document_type', faceted=True)
    status = indexes.CharField(model_attr='status', faceted=True)
    created_at = indexes.DateTimeField(model_attr='created_at')
    updated_at = indexes.DateTimeField(model_attr='updated_at')
    uploaded_by = indexes.CharField(model_attr='uploaded_by', null=True)
    keywords = indexes.CharField(model_attr='keywords', null=True)
    content = indexes.CharField()
    
    def get_model(self):
        """Return the model class for this index"""
        return Document
    
    def index_queryset(self, using=None):
        """Return the queryset to use for indexing"""
        return self.get_model().objects.filter(is_latest_version=True)
    
    def prepare_uploaded_by(self, obj):
        """Prepare the uploaded_by field"""
        if obj.uploaded_by:
            return obj.uploaded_by.username
        return None
    
    def prepare_content(self, obj):
        """Extract text content from document file"""
        if not obj.file:
            return ""
        
        file_path = os.path.join(settings.MEDIA_ROOT, obj.file.name)
        
        if not os.path.exists(file_path):
            return ""
        
        # Get file extension
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()
        
        try:
            # Extract text from document
            text = textract.process(file_path).decode('utf-8', errors='ignore')
            return text
        except Exception as e:
            # Log the error but don't fail indexing
            print(f"Error extracting text from {file_path}: {e}")
            return ""
