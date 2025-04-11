"""
Document version management utilities
"""
import os
import difflib
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

from documents.models import Document

class DocumentVersionManager:
    """Manager for document version operations"""
    
    def __init__(self, user=None):
        """Initialize the version manager
        
        Args:
            user: The user performing the version operations
        """
        self.user = user
    
    def create_new_version(self, document, file=None, version_notes=''):
        """Create a new version of a document
        
        Args:
            document: The document to create a new version of
            file: New file content (optional)
            version_notes: Notes about the version changes
        
        Returns:
            The new document version
        """
        # Get the parent document (if this is already a version)
        parent = document.parent_document or document
        
        # Get the latest version number
        latest_version = self._get_latest_version_number(parent)
        
        # Create new version
        with transaction.atomic():
            # Update previous versions to not be latest
            if document.is_latest_version:
                document.is_latest_version = False
                document.save()
            
            if parent.is_latest_version and parent != document:
                parent.is_latest_version = False
                parent.save()
            
            # Create new version
            new_version = Document.objects.create(
                title=document.title,
                description=document.description,
                document_type=document.document_type,
                application=document.application,
                category=document.category,
                keywords=document.keywords,
                status='draft',  # New versions always start as drafts
                access_level=document.access_level,
                is_confidential=document.is_confidential,
                expiration_date=document.expiration_date,
                uploaded_by=self.user or document.uploaded_by,
                last_modified_by=self.user or document.last_modified_by,
                parent_document=parent,
                version=latest_version + 1,
                version_notes=version_notes,
                is_latest_version=True
            )
            
            # Copy file if not provided
            if file:
                new_version.file = file
            else:
                # Copy file from previous version
                if document.file:
                    file_name = os.path.basename(document.file.name)
                    new_version.file.save(
                        file_name,
                        document.file.open(),
                        save=True
                    )
            
            # Copy tags
            new_version.tags.set(document.tags.all())
            
            # Send notifications
            try:
                from documents.utils.notification_manager import DocumentNotificationManager
                notification_manager = DocumentNotificationManager(user=self.user)
                notification_manager.notify_new_version_created(new_version, document)
            except ImportError:
                # Notification system not available, continue without notifications
                pass
            
            return new_version
    
    def get_version_history(self, document):
        """Get version history of a document
        
        Args:
            document: The document to get version history for
        
        Returns:
            List of document versions ordered by version number
        """
        # Get the parent document (if this is already a version)
        parent = document.parent_document or document
        
        # Get all versions
        versions = list(Document.objects.filter(parent_document=parent))
        
        # Add parent to the list if it's not already there
        if parent not in versions:
            versions.append(parent)
        
        # Sort by version number
        versions.sort(key=lambda x: x.version)
        
        return versions
    
    def compare_versions(self, document1, document2):
        """Compare two document versions
        
        Args:
            document1: First document version
            document2: Second document version
        
        Returns:
            Dictionary with comparison results
        """
        # Check if documents are related
        if document1.parent_document != document2.parent_document and document1 != document2.parent_document and document2 != document1.parent_document:
            raise ValidationError("Documents are not related versions")
        
        # Compare metadata
        metadata_changes = {}
        
        # Fields to compare
        fields_to_compare = [
            'title', 'description', 'document_type', 'status', 
            'access_level', 'is_confidential', 'expiration_date'
        ]
        
        for field in fields_to_compare:
            value1 = getattr(document1, field)
            value2 = getattr(document2, field)
            
            if value1 != value2:
                metadata_changes[field] = {
                    'old': value1,
                    'new': value2
                }
        
        # Compare file content if possible
        content_changes = None
        can_compare_content = False
        
        if document1.file and document2.file:
            try:
                # Read file content
                content1 = document1.file.read().decode('utf-8').splitlines()
                document1.file.seek(0)  # Reset file pointer
                
                content2 = document2.file.read().decode('utf-8').splitlines()
                document2.file.seek(0)  # Reset file pointer
                
                # Generate diff
                diff = list(difflib.unified_diff(
                    content1, 
                    content2,
                    fromfile=f"Version {document1.version}",
                    tofile=f"Version {document2.version}",
                    lineterm=''
                ))
                
                # Calculate statistics
                lines_added = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
                lines_removed = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))
                lines_changed = min(lines_added, lines_removed)
                lines_added -= lines_changed
                lines_removed -= lines_changed
                
                content_changes = {
                    'diff': '\n'.join(diff),
                    'statistics': {
                        'lines_before': len(content1),
                        'lines_after': len(content2),
                        'lines_added': lines_added,
                        'lines_removed': lines_removed,
                        'lines_changed': lines_changed
                    }
                }
                
                can_compare_content = True
            except UnicodeDecodeError:
                # Binary files, can't compare content
                content_changes = {
                    'diff': None,
                    'statistics': {
                        'binary_files': True
                    }
                }
        
        return {
            'metadata_changes': metadata_changes,
            'content_changes': content_changes,
            'can_compare_content': can_compare_content
        }
    
    def rollback_to_version(self, document):
        """Rollback to a specific version
        
        Args:
            document: The document version to roll back to
        
        Returns:
            The new document version
        """
        # Create a new version based on the rollback target
        new_version = self.create_new_version(
            document,
            version_notes=f"Rollback to version {document.version}"
        )
        
        return new_version
    
    def _get_latest_version_number(self, parent_document):
        """Get the latest version number for a document
        
        Args:
            parent_document: The parent document
        
        Returns:
            The latest version number
        """
        # Get the latest version
        latest_version = Document.objects.filter(parent_document=parent_document).order_by('-version').first()
        
        # If no versions exist, use the parent's version
        if not latest_version:
            return parent_document.version
        
        return latest_version.version
