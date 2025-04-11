"""
Document approval workflow utilities for the document management system
"""
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from documents.models import Document, DocumentApproval

User = get_user_model()

class ApprovalWorkflowManager:
    """Manager for document approval workflow operations"""
    
    def __init__(self, user=None):
        """Initialize the approval workflow manager
        
        Args:
            user: The user performing the approval operations
        """
        self.user = user
    
    def request_approval(self, document, reviewers=None, approval_level=1, comments=None):
        """Request approval for a document
        
        Args:
            document: The document to request approval for
            reviewers: List of users to review the document (optional)
            approval_level: The level of approval required (1=basic, 2=manager, 3=executive)
            comments: Comments for the approval request
        
        Returns:
            List of created approval requests
        """
        if document.status not in ['draft', 'rejected']:
            raise ValidationError(f"Cannot request approval for document with status '{document.status}'")
        
        # Update document status
        with transaction.atomic():
            document.status = 'pending_approval'
            document.save()
            
            # Create approval requests
            approvals = []
            
            # If no reviewers specified, use default reviewers based on approval level
            if not reviewers:
                reviewers = self._get_default_reviewers(approval_level)
            
            # Create approval requests for each reviewer
            for reviewer in reviewers:
                approval = DocumentApproval.objects.create(
                    document=document,
                    reviewer=reviewer,
                    requested_by=self.user,
                    approval_level=approval_level,
                    comments=comments,
                    status='pending'
                )
                approvals.append(approval)
            
            # Send notifications
            try:
                from documents.utils.notification_manager import DocumentNotificationManager
                notification_manager = DocumentNotificationManager(user=self.user)
                notification_manager.notify_approval_requested(document, approvals)
            except ImportError:
                # Notification system not available, continue without notifications
                pass
            
            return approvals
    
    def approve_document(self, approval, comments=None):
        """Approve a document
        
        Args:
            approval: The approval request to approve
            comments: Comments for the approval
        
        Returns:
            The updated approval request
        """
        if approval.status != 'pending':
            raise ValidationError(f"Cannot approve a request with status '{approval.status}'")
        
        with transaction.atomic():
            # Update approval
            approval.status = 'approved'
            approval.approval_date = timezone.now()
            approval.approval_comments = comments
            approval.save()
            
            # Check if all approvals are complete
            document = approval.document
            pending_approvals = document.approvals.filter(status='pending').count()
            
            # If no pending approvals, update document status
            if pending_approvals == 0:
                document.status = 'approved'
                document.save()
            
            # Send notifications
            try:
                from documents.utils.notification_manager import DocumentNotificationManager
                notification_manager = DocumentNotificationManager(user=self.user)
                notification_manager.notify_document_approved(approval)
            except ImportError:
                # Notification system not available, continue without notifications
                pass
            
            return approval
    
    def reject_document(self, approval, comments=None):
        """Reject a document
        
        Args:
            approval: The approval request to reject
            comments: Comments for the rejection
        
        Returns:
            The updated approval request
        """
        if approval.status != 'pending':
            raise ValidationError(f"Cannot reject a request with status '{approval.status}'")
        
        with transaction.atomic():
            # Update approval
            approval.status = 'rejected'
            approval.approval_date = timezone.now()
            approval.approval_comments = comments
            approval.save()
            
            # Update document status
            document = approval.document
            document.status = 'rejected'
            document.save()
            
            # Cancel other pending approvals
            document.approvals.filter(status='pending').update(
                status='cancelled',
                approval_date=timezone.now(),
                approval_comments='Cancelled due to rejection by another reviewer'
            )
            
            # Send notifications
            try:
                from documents.utils.notification_manager import DocumentNotificationManager
                notification_manager = DocumentNotificationManager(user=self.user)
                notification_manager.notify_document_rejected(approval)
            except ImportError:
                # Notification system not available, continue without notifications
                pass
            
            return approval
    
    def cancel_approval_request(self, document):
        """Cancel all pending approval requests for a document
        
        Args:
            document: The document to cancel approval requests for
        
        Returns:
            Number of cancelled approval requests
        """
        if document.status != 'pending_approval':
            raise ValidationError(f"Cannot cancel approvals for document with status '{document.status}'")
        
        with transaction.atomic():
            # Update document status
            document.status = 'draft'
            document.save()
            
            # Cancel pending approvals
            cancelled = document.approvals.filter(status='pending').update(
                status='cancelled',
                approval_date=timezone.now(),
                approval_comments='Cancelled by document owner'
            )
            
            return cancelled
    
    def get_approval_status(self, document):
        """Get the approval status for a document
        
        Args:
            document: The document to get approval status for
        
        Returns:
            Dictionary with approval status information
        """
        approvals = document.approvals.all()
        
        # Count approvals by status
        total = approvals.count()
        pending = approvals.filter(status='pending').count()
        approved = approvals.filter(status='approved').count()
        rejected = approvals.filter(status='rejected').count()
        cancelled = approvals.filter(status='cancelled').count()
        
        # Get approval history
        history = []
        for approval in approvals:
            history.append({
                'id': approval.id,
                'reviewer': {
                    'id': approval.reviewer.id,
                    'name': approval.reviewer.get_full_name(),
                    'email': approval.reviewer.email
                },
                'status': approval.status,
                'requested_date': approval.created_at,
                'approval_date': approval.approval_date,
                'comments': approval.comments,
                'approval_comments': approval.approval_comments,
                'approval_level': approval.approval_level
            })
        
        return {
            'document_status': document.status,
            'total_approvals': total,
            'pending_approvals': pending,
            'approved_approvals': approved,
            'rejected_approvals': rejected,
            'cancelled_approvals': cancelled,
            'is_fully_approved': document.status == 'approved',
            'is_rejected': document.status == 'rejected',
            'approval_history': history
        }
    
    def reassign_reviewer(self, approval, new_reviewer):
        """Reassign an approval request to a different reviewer
        
        Args:
            approval: The approval request to reassign
            new_reviewer: The new reviewer
        
        Returns:
            The updated approval request
        """
        if approval.status != 'pending':
            raise ValidationError(f"Cannot reassign a request with status '{approval.status}'")
        
        approval.reviewer = new_reviewer
        approval.save()
        
        return approval
    
    def add_reviewer(self, document, reviewer, approval_level=1, comments=None):
        """Add a new reviewer to a document
        
        Args:
            document: The document to add a reviewer to
            reviewer: The user to add as a reviewer
            approval_level: The level of approval required
            comments: Comments for the approval request
        
        Returns:
            The created approval request
        """
        if document.status != 'pending_approval':
            raise ValidationError(f"Cannot add reviewer to document with status '{document.status}'")
        
        approval = DocumentApproval.objects.create(
            document=document,
            reviewer=reviewer,
            requested_by=self.user,
            approval_level=approval_level,
            comments=comments,
            status='pending'
        )
        
        return approval
    
    def _get_default_reviewers(self, approval_level):
        """Get default reviewers based on approval level
        
        Args:
            approval_level: The level of approval required
        
        Returns:
            List of users to review the document
        """
        # In a real system, this would query users based on roles or permissions
        # For now, we'll just return admin users
        return User.objects.filter(is_staff=True)[:3]  # Limit to 3 reviewers
