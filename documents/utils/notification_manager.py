"""
Notification manager for document-related events
"""
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
from django.core.mail import send_mail

from notifications.models import Notification

class DocumentNotificationManager:
    """Manager for document-related notifications"""
    
    def __init__(self, user=None):
        """Initialize the notification manager
        
        Args:
            user: The user triggering the notification
        """
        self.user = user
    
    def notify_document_uploaded(self, document):
        """Send notification when a document is uploaded
        
        Args:
            document: The uploaded document
        """
        # Create in-app notification for document owner and relevant users
        self._create_notification(
            recipient=document.uploaded_by,
            title="Document Uploaded",
            message=f"Your document '{document.title}' has been uploaded successfully.",
            document=document,
            notification_type="document_uploaded"
        )
        
        # If document is associated with an application, notify relevant parties
        if document.application:
            # Notify application owner
            if document.application.borrower and document.application.borrower.user:
                self._create_notification(
                    recipient=document.application.borrower.user,
                    title="New Document Available",
                    message=f"A new document '{document.title}' has been uploaded to your application.",
                    document=document,
                    notification_type="document_uploaded"
                )
            
            # Notify assigned broker
            if document.application.broker and document.application.broker.user:
                self._create_notification(
                    recipient=document.application.broker.user,
                    title="New Document Available",
                    message=f"A new document '{document.title}' has been uploaded to application #{document.application.id}.",
                    document=document,
                    notification_type="document_uploaded"
                )
    
    def notify_approval_requested(self, document, approvals):
        """Send notification when document approval is requested
        
        Args:
            document: The document requiring approval
            approvals: List of approval requests
        """
        # Notify document owner
        self._create_notification(
            recipient=document.uploaded_by,
            title="Approval Process Started",
            message=f"Approval process has been initiated for document '{document.title}'.",
            document=document,
            notification_type="approval_requested"
        )
        
        # Notify each reviewer
        for approval in approvals:
            # Create in-app notification
            self._create_notification(
                recipient=approval.reviewer,
                title="Document Approval Requested",
                message=f"Your approval is requested for document '{document.title}'.",
                document=document,
                notification_type="approval_requested",
                approval=approval
            )
            
            # Send email notification
            self._send_email_notification(
                recipient=approval.reviewer,
                subject="Document Approval Requested",
                template="documents/email/approval_requested.html",
                context={
                    "reviewer_name": approval.reviewer.get_full_name() or approval.reviewer.username,
                    "document_title": document.title,
                    "requested_by": self.user.get_full_name() if self.user else "The system",
                    "comments": approval.comments,
                    "approval_level": approval.get_approval_level_display(),
                    "approval_url": self._get_approval_url(approval)
                }
            )
    
    def notify_document_approved(self, approval):
        """Send notification when a document is approved
        
        Args:
            approval: The approval that was granted
        """
        document = approval.document
        
        # Notify document owner
        self._create_notification(
            recipient=document.uploaded_by,
            title="Document Approved",
            message=f"Document '{document.title}' has been approved by {approval.reviewer.get_full_name()}.",
            document=document,
            notification_type="document_approved"
        )
        
        # If all approvals are complete, send final approval notification
        if document.status == 'approved':
            self._create_notification(
                recipient=document.uploaded_by,
                title="Document Fully Approved",
                message=f"Document '{document.title}' has received all required approvals.",
                document=document,
                notification_type="document_fully_approved"
            )
            
            # If document is associated with an application, notify relevant parties
            if document.application:
                # Notify application owner
                if document.application.borrower and document.application.borrower.user:
                    self._create_notification(
                        recipient=document.application.borrower.user,
                        title="Document Approved",
                        message=f"Document '{document.title}' has been approved.",
                        document=document,
                        notification_type="document_approved"
                    )
                
                # Notify assigned broker
                if document.application.broker and document.application.broker.user:
                    self._create_notification(
                        recipient=document.application.broker.user,
                        title="Document Approved",
                        message=f"Document '{document.title}' for application #{document.application.id} has been approved.",
                        document=document,
                        notification_type="document_approved"
                    )
    
    def notify_document_rejected(self, approval):
        """Send notification when a document is rejected
        
        Args:
            approval: The approval that was rejected
        """
        document = approval.document
        
        # Notify document owner
        self._create_notification(
            recipient=document.uploaded_by,
            title="Document Rejected",
            message=f"Document '{document.title}' has been rejected by {approval.reviewer.get_full_name()}.",
            document=document,
            notification_type="document_rejected"
        )
        
        # Send email notification
        self._send_email_notification(
            recipient=document.uploaded_by,
            subject="Document Rejected",
            template="documents/email/document_rejected.html",
            context={
                "recipient_name": document.uploaded_by.get_full_name() or document.uploaded_by.username,
                "document_title": document.title,
                "reviewer_name": approval.reviewer.get_full_name() or approval.reviewer.username,
                "rejection_comments": approval.approval_comments,
                "document_url": self._get_document_url(document)
            }
        )
        
        # If document is associated with an application, notify relevant parties
        if document.application:
            # Notify application owner
            if document.application.borrower and document.application.borrower.user:
                self._create_notification(
                    recipient=document.application.borrower.user,
                    title="Document Rejected",
                    message=f"Document '{document.title}' has been rejected.",
                    document=document,
                    notification_type="document_rejected"
                )
            
            # Notify assigned broker
            if document.application.broker and document.application.broker.user:
                self._create_notification(
                    recipient=document.application.broker.user,
                    title="Document Rejected",
                    message=f"Document '{document.title}' for application #{document.application.id} has been rejected.",
                    document=document,
                    notification_type="document_rejected"
                )
    
    def notify_document_expiring_soon(self, document, days_remaining):
        """Send notification when a document is about to expire
        
        Args:
            document: The document that is expiring
            days_remaining: Number of days until expiration
        """
        # Notify document owner
        self._create_notification(
            recipient=document.uploaded_by,
            title="Document Expiring Soon",
            message=f"Document '{document.title}' will expire in {days_remaining} days.",
            document=document,
            notification_type="document_expiring"
        )
        
        # Send email notification
        self._send_email_notification(
            recipient=document.uploaded_by,
            subject="Document Expiring Soon",
            template="documents/email/document_expiring.html",
            context={
                "recipient_name": document.uploaded_by.get_full_name() or document.uploaded_by.username,
                "document_title": document.title,
                "days_remaining": days_remaining,
                "expiration_date": document.expiration_date,
                "document_url": self._get_document_url(document)
            }
        )
        
        # If document is associated with an application, notify relevant parties
        if document.application:
            # Notify assigned broker
            if document.application.broker and document.application.broker.user:
                self._create_notification(
                    recipient=document.application.broker.user,
                    title="Document Expiring Soon",
                    message=f"Document '{document.title}' for application #{document.application.id} will expire in {days_remaining} days.",
                    document=document,
                    notification_type="document_expiring"
                )
    
    def notify_new_version_created(self, document, previous_version):
        """Send notification when a new document version is created
        
        Args:
            document: The new document version
            previous_version: The previous version of the document
        """
        # Notify document owner
        self._create_notification(
            recipient=document.uploaded_by,
            title="New Document Version Created",
            message=f"Version {document.version} of document '{document.title}' has been created.",
            document=document,
            notification_type="new_version"
        )
        
        # If document is associated with an application, notify relevant parties
        if document.application:
            # Notify application owner
            if document.application.borrower and document.application.borrower.user:
                self._create_notification(
                    recipient=document.application.borrower.user,
                    title="Document Updated",
                    message=f"Document '{document.title}' has been updated to version {document.version}.",
                    document=document,
                    notification_type="new_version"
                )
            
            # Notify assigned broker
            if document.application.broker and document.application.broker.user:
                self._create_notification(
                    recipient=document.application.broker.user,
                    title="Document Updated",
                    message=f"Document '{document.title}' for application #{document.application.id} has been updated to version {document.version}.",
                    document=document,
                    notification_type="new_version"
                )
    
    def notify_signature_requested(self, document, signature_requests):
        """Send notification when signatures are requested
        
        Args:
            document: The document requiring signatures
            signature_requests: List of signature requests
        """
        # Notify document owner
        self._create_notification(
            recipient=document.uploaded_by,
            title="Signature Process Started",
            message=f"Signature process has been initiated for document '{document.title}'.",
            document=document,
            notification_type="signature_requested"
        )
        
        # Notify each signer
        for request in signature_requests:
            # Create in-app notification
            self._create_notification(
                recipient=request.signer,
                title="Document Signature Requested",
                message=f"Your signature is requested for document '{document.title}'.",
                document=document,
                notification_type="signature_requested",
                signature_request=request
            )
            
            # Send email notification
            self._send_email_notification(
                recipient=request.signer,
                subject="Document Signature Requested",
                template="documents/email/signature_requested.html",
                context={
                    "signer_name": request.signer.get_full_name() or request.signer.username,
                    "document_title": document.title,
                    "requested_by": self.user.get_full_name() if self.user else "The system",
                    "message": request.message,
                    "due_date": request.due_date,
                    "signature_url": self._get_signature_url(request)
                }
            )
    
    def notify_document_signed(self, signature):
        """Send notification when a document is signed
        
        Args:
            signature: The signature that was created
        """
        document = signature.document
        
        # Notify document owner
        self._create_notification(
            recipient=document.uploaded_by,
            title="Document Signed",
            message=f"Document '{document.title}' has been signed by {signature.signer.get_full_name()}.",
            document=document,
            notification_type="document_signed"
        )
        
        # If all signatures are complete, send final signed notification
        if document.status == 'signed':
            self._create_notification(
                recipient=document.uploaded_by,
                title="Document Fully Signed",
                message=f"Document '{document.title}' has received all required signatures.",
                document=document,
                notification_type="document_fully_signed"
            )
            
            # If document is associated with an application, notify relevant parties
            if document.application:
                # Notify application owner
                if document.application.borrower and document.application.borrower.user:
                    self._create_notification(
                        recipient=document.application.borrower.user,
                        title="Document Signed",
                        message=f"Document '{document.title}' has been signed by all parties.",
                        document=document,
                        notification_type="document_signed"
                    )
                
                # Notify assigned broker
                if document.application.broker and document.application.broker.user:
                    self._create_notification(
                        recipient=document.application.broker.user,
                        title="Document Signed",
                        message=f"Document '{document.title}' for application #{document.application.id} has been signed by all parties.",
                        document=document,
                        notification_type="document_signed"
                    )
    
    def notify_signature_declined(self, signature_request):
        """Send notification when a signature is declined
        
        Args:
            signature_request: The signature request that was declined
        """
        document = signature_request.document
        
        # Notify document owner
        self._create_notification(
            recipient=document.uploaded_by,
            title="Signature Declined",
            message=f"Signature for document '{document.title}' has been declined by {signature_request.signer.get_full_name()}.",
            document=document,
            notification_type="signature_declined"
        )
        
        # Send email notification
        self._send_email_notification(
            recipient=document.uploaded_by,
            subject="Document Signature Declined",
            template="documents/email/signature_declined.html",
            context={
                "recipient_name": document.uploaded_by.get_full_name() or document.uploaded_by.username,
                "document_title": document.title,
                "signer_name": signature_request.signer.get_full_name() or signature_request.signer.username,
                "decline_reason": signature_request.decline_reason,
                "document_url": self._get_document_url(document)
            }
        )
        
        # If document is associated with an application, notify relevant parties
        if document.application:
            # Notify assigned broker
            if document.application.broker and document.application.broker.user:
                self._create_notification(
                    recipient=document.application.broker.user,
                    title="Signature Declined",
                    message=f"Signature for document '{document.title}' for application #{document.application.id} has been declined.",
                    document=document,
                    notification_type="signature_declined"
                )
    
    def notify_signature_request_cancelled(self, signature_request):
        """Send notification when a signature request is cancelled
        
        Args:
            signature_request: The signature request that was cancelled
        """
        document = signature_request.document
        
        # Notify signer
        self._create_notification(
            recipient=signature_request.signer,
            title="Signature Request Cancelled",
            message=f"Signature request for document '{document.title}' has been cancelled.",
            document=document,
            notification_type="signature_cancelled"
        )
        
        # Send email notification
        self._send_email_notification(
            recipient=signature_request.signer,
            subject="Signature Request Cancelled",
            template="documents/email/signature_cancelled.html",
            context={
                "recipient_name": signature_request.signer.get_full_name() or signature_request.signer.username,
                "document_title": document.title,
                "cancelled_by": self.user.get_full_name() if self.user else "The system"
            }
        )
    
    def _create_notification(self, recipient, title, message, document, notification_type, approval=None, signature_request=None):
        """Create an in-app notification
        
        Args:
            recipient: User to receive the notification
            title: Notification title
            message: Notification message
            document: Related document
            notification_type: Type of notification
            approval: Related approval (optional)
            signature_request: Related signature request (optional)
        """
        # Create notification object
        notification = Notification.objects.create(
            recipient=recipient,
            sender=self.user,
            title=title,
            message=message,
            notification_type=notification_type,
            is_read=False,
            content_object=document
        )
        
        # Add additional metadata
        metadata = {
            'document_id': document.id,
            'document_title': document.title,
            'document_type': document.document_type
        }
        
        if document.application:
            metadata['application_id'] = document.application.id
        
        if approval:
            metadata['approval_id'] = approval.id
            metadata['approval_status'] = approval.status
        
        if signature_request:
            metadata['signature_request_id'] = signature_request.id
            metadata['signature_request_status'] = signature_request.status
        
        notification.metadata = metadata
        notification.save()
        
        return notification
    
    def _send_email_notification(self, recipient, subject, template, context):
        """Send an email notification
        
        Args:
            recipient: User to receive the email
            subject: Email subject
            template: Email template path
            context: Template context
        """
        # Only send if recipient has an email and email notifications are enabled
        if not recipient.email or not getattr(settings, 'ENABLE_EMAIL_NOTIFICATIONS', False):
            return
        
        # Add common context variables
        context.update({
            'site_name': getattr(settings, 'SITE_NAME', 'Loan Management System'),
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        })
        
        # Render email content
        html_content = render_to_string(template, context)
        
        # Send email
        try:
            send_mail(
                subject=subject,
                message="",  # Plain text version (empty for HTML-only emails)
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                html_message=html_content,
                fail_silently=False
            )
        except Exception as e:
            # Log the error but don't raise it
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send email notification: {str(e)}")
    
    def _get_approval_url(self, approval):
        """Get URL for approval action
        
        Args:
            approval: The approval object
        
        Returns:
            URL for approval action
        """
        base_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        return f"{base_url}/documents/approvals/{approval.id}/"
    
    def _get_document_url(self, document):
        """Get URL for document
        
        Args:
            document: The document object
        
        Returns:
            URL for document
        """
        base_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        return f"{base_url}/documents/{document.id}/"
    
    def _get_signature_url(self, signature_request):
        """Get URL for signature action
        
        Args:
            signature_request: The signature request object
        
        Returns:
            URL for signature action
        """
        base_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        return f"{base_url}/documents/sign/{signature_request.signature_token}/"
