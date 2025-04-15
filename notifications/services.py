"""
Notification services for creating and managing notifications
"""
from django.utils import timezone
from .models import Notification

def create_notification(recipient, title, message, notification_type='system', related_application=None):
    """
    Create a new notification
    
    Args:
        recipient: User who will receive the notification
        title: Notification title
        message: Notification message
        notification_type: Type of notification (system, email, alert, etc.)
        related_application: Optional related application
        
    Returns:
        Created notification object
    """
    notification = Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        type=notification_type,
        related_application=related_application,
        trigger_date=timezone.now()
    )
    
    return notification

def create_document_approval_notification(approval):
    """
    Create notification for document approval events
    
    Args:
        approval: DocumentApproval object
        
    Returns:
        Created notification object
    """
    document = approval.document
    
    # Notification for reviewer when approval is requested
    if approval.status == 'pending':
        title = f"Document Approval Requested: {document.title}"
        message = f"You have been requested to review and approve the document '{document.title}' by {approval.requested_by.get_full_name() or approval.requested_by.username}."
        
        return create_notification(
            recipient=approval.reviewer,
            title=title,
            message=message,
            notification_type='alert',
            related_application=document.application
        )
    
    # Notification for requester when approval is completed
    elif approval.status in ['approved', 'rejected']:
        action = "approved" if approval.status == 'approved' else "rejected"
        title = f"Document {action.capitalize()}: {document.title}"
        message = f"Your document '{document.title}' has been {action} by {approval.reviewer.get_full_name() or approval.reviewer.username}."
        if approval.comments:
            message += f" Comments: {approval.comments}"
        
        return create_notification(
            recipient=approval.requested_by,
            title=title,
            message=message,
            notification_type='alert',
            related_application=document.application
        )
    
    # Notification for reviewer when approval is reassigned
    elif approval.status == 'reassigned':
        title = f"Document Approval Reassigned: {document.title}"
        message = f"A document approval request for '{document.title}' has been reassigned to you by {approval.requested_by.get_full_name() or approval.requested_by.username}."
        
        return create_notification(
            recipient=approval.reviewer,
            title=title,
            message=message,
            notification_type='alert',
            related_application=document.application
        )
    
    return None

def create_signature_request_notification(signature_request):
    """
    Create notification for signature request events
    
    Args:
        signature_request: DocumentSignatureRequest object
        
    Returns:
        Created notification object
    """
    document = signature_request.document
    
    # Notification for signer when signature is requested
    if signature_request.status == 'pending':
        title = f"Signature Requested: {document.title}"
        message = f"You have been requested to sign the document '{document.title}' by {signature_request.requested_by.get_full_name() or signature_request.requested_by.username}."
        
        return create_notification(
            recipient=signature_request.signer,
            title=title,
            message=message,
            notification_type='alert',
            related_application=document.application
        )
    
    # Notification for requester when signature is completed
    elif signature_request.status in ['signed', 'declined']:
        action = "signed" if signature_request.status == 'signed' else "declined to sign"
        title = f"Document {action.capitalize()}: {document.title}"
        message = f"The document '{document.title}' has been {action} by {signature_request.signer.get_full_name() or signature_request.signer.username}."
        if signature_request.decline_reason:
            message += f" Reason: {signature_request.decline_reason}"
        
        return create_notification(
            recipient=signature_request.requested_by,
            title=title,
            message=message,
            notification_type='alert',
            related_application=document.application
        )
    
    return None
