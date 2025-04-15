from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from rest_framework.response import Response
from django.utils import timezone
from .models import Document, DocumentApproval
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from notifications.services import create_document_approval_notification

User = get_user_model()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def request_document_approval(request, document_id):
    """Request approval for a document"""
    try:
        document = Document.objects.get(pk=document_id)
    except Document.DoesNotExist:
        return Response({"detail": "Document not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Validate request data
    if 'reviewer_id' not in request.data:
        return Response({"reviewer_id": "This field is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    approval_level = request.data.get('approval_level', 1)
    try:
        approval_level = int(approval_level)
        if approval_level < 1 or approval_level > 5:
            return Response({"approval_level": "Must be between 1 and 5"}, status=status.HTTP_400_BAD_REQUEST)
    except ValueError:
        return Response({"approval_level": "Must be a number"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get reviewer
    try:
        reviewer = User.objects.get(pk=request.data['reviewer_id'])
    except User.DoesNotExist:
        return Response({"reviewer_id": "Reviewer not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if there's already a pending approval request for this document and reviewer
    existing_approval = DocumentApproval.objects.filter(
        document=document,
        reviewer=reviewer,
        status='pending'
    ).first()
    
    if existing_approval:
        return Response(
            {"detail": "There is already a pending approval request for this document and reviewer"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create approval request
    approval = DocumentApproval.objects.create(
        document=document,
        reviewer=reviewer,
        requested_by=request.user,
        status='pending',
        requested_date=timezone.now(),
        approval_level=approval_level
    )
    
    # Create notification for the reviewer
    create_document_approval_notification(approval)
    
    return Response({
        "id": approval.id,
        "document": document.id,
        "reviewer": {
            "id": reviewer.id,
            "username": reviewer.username,
            "email": reviewer.email
        },
        "status": "pending",
        "approval_level": approval_level,
        "requested_date": approval.requested_date
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def respond_to_approval(request, approval_id):
    """Respond to an approval request (approve or reject)"""
    approval = get_object_or_404(DocumentApproval, pk=approval_id)
    
    # Check if the current user is the reviewer
    if approval.reviewer != request.user:
        return Response(
            {"detail": "Only the assigned reviewer can respond to this approval request"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check if the approval is still pending
    if approval.status != 'pending':
        return Response(
            {"detail": f"This approval request has already been {approval.status}"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate request data
    if 'status' not in request.data:
        return Response({"status": "This field is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.data['status'] not in ['approved', 'rejected']:
        return Response(
            {"status": "Status must be 'approved' or 'rejected'"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # If rejecting, comments are required
    if request.data['status'] == 'rejected' and not request.data.get('comments'):
        return Response(
            {"comments": "Comments are required when rejecting an approval request"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update approval
    approval.status = request.data['status']
    approval.comments = request.data.get('comments', '')
    approval.response_date = timezone.now()
    approval.save()
    
    # Update document status if approved
    if approval.status == 'approved':
        # Check if all required approvals are complete
        pending_approvals = DocumentApproval.objects.filter(
            document=approval.document,
            status='pending'
        ).count()
        
        if pending_approvals == 0:
            approval.document.status = 'approved'
            approval.document.save()
    
    # Update document status if rejected
    if approval.status == 'rejected':
        approval.document.status = 'rejected'
        approval.document.save()
    
    # Create notification for the requester
    create_document_approval_notification(approval)
    
    return Response({
        "id": approval.id,
        "document": approval.document.id,
        "status": approval.status,
        "comments": approval.comments,
        "response_date": approval.response_date
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_approval_request(request, approval_id):
    """Cancel an approval request"""
    approval = get_object_or_404(DocumentApproval, pk=approval_id)
    
    # Check if the current user is the requester
    if approval.requested_by != request.user:
        return Response(
            {"detail": "Only the requester can cancel this approval request"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check if the approval is still pending
    if approval.status != 'pending':
        return Response(
            {"detail": f"This approval request has already been {approval.status}"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Cancel approval
    approval.status = 'cancelled'
    approval.response_date = timezone.now()
    approval.save()
    
    return Response({
        "id": approval.id,
        "document": approval.document.id,
        "status": "cancelled",
        "response_date": approval.response_date
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reassign_approval(request, approval_id):
    """Reassign an approval request to another reviewer"""
    approval = get_object_or_404(DocumentApproval, pk=approval_id)
    
    # Check if the current user is the requester
    if approval.requested_by != request.user:
        return Response(
            {"detail": "Only the requester can reassign this approval request"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check if the approval is still pending
    if approval.status != 'pending':
        return Response(
            {"detail": f"This approval request has already been {approval.status}"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate request data
    if 'reviewer_id' not in request.data:
        return Response({"reviewer_id": "This field is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get new reviewer
    try:
        new_reviewer = User.objects.get(pk=request.data['reviewer_id'])
    except User.DoesNotExist:
        return Response({"reviewer_id": "Reviewer not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Store old reviewer for notification
    old_reviewer = approval.reviewer
    
    # Update approval
    approval.reviewer = new_reviewer
    approval.save()
    
    # Create notification for the new reviewer
    approval.status = 'reassigned'  # Temporary status for notification
    create_document_approval_notification(approval)
    approval.status = 'pending'  # Reset to actual status
    approval.save()
    
    return Response({
        "id": approval.id,
        "document": approval.document.id,
        "reviewer": {
            "id": new_reviewer.id,
            "username": new_reviewer.username,
            "email": new_reviewer.email
        },
        "status": approval.status
    }, status=status.HTTP_200_OK)
