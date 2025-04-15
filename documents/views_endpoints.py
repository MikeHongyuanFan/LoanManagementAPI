from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from rest_framework.response import Response
from django.utils import timezone
from .models import Document, DocumentMetadata, CustomMetadataField, DocumentSignatureRequest, DocumentSignature
from datetime import datetime
import hashlib
import time
from notifications.services import create_signature_request_notification

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def document_metadata_bulk_update(request, pk):
    """Bulk update document metadata"""
    try:
        document = Document.objects.get(pk=pk)
    except Document.DoesNotExist:
        return Response({"detail": "Document not found"}, status=status.HTTP_404_NOT_FOUND)
    
    metadata_list = request.data.get('metadata', [])
    if not isinstance(metadata_list, list):
        return Response({"metadata": "Must be a list"}, status=status.HTTP_400_BAD_REQUEST)
    
    results = []
    errors = []
    
    for item in metadata_list:
        if not item.get('id') and not (item.get('field_id') and item.get('document')):
            errors.append({"error": "Either id or both field_id and document are required", "item": item})
            continue
        
        if item.get('value') == '':
            errors.append({"error": "Value cannot be empty", "item": item})
            continue
        
        # Update existing metadata
        if item.get('id'):
            try:
                metadata = DocumentMetadata.objects.get(pk=item['id'])
                
                # Validate value based on field type
                field = metadata.field
                value = item.get('value')
                
                # Validate based on field type
                if field.field_type == 'number':
                    try:
                        float(value)
                    except ValueError:
                        errors.append({"error": "Value must be a number", "item": item})
                        continue
                        
                elif field.field_type == 'date':
                    try:
                        datetime.strptime(value, '%Y-%m-%d')
                    except ValueError:
                        errors.append({"error": "Value must be a valid date in YYYY-MM-DD format", "item": item})
                        continue
                        
                elif field.field_type == 'select' and field.options:
                    if value not in field.options:
                        errors.append({"error": f"Value must be one of: {', '.join(field.options)}", "item": item})
                        continue
                
                metadata.value = value
                metadata.save()
                results.append({"id": metadata.id, "status": "updated"})
                
            except DocumentMetadata.DoesNotExist:
                errors.append({"error": "Metadata not found", "item": item})
        
        # Create new metadata
        else:
            try:
                field = CustomMetadataField.objects.get(pk=item['field_id'])
                
                # Validate value based on field type
                value = item.get('value')
                
                # Validate based on field type
                if field.field_type == 'number':
                    try:
                        float(value)
                    except ValueError:
                        errors.append({"error": "Value must be a number", "item": item})
                        continue
                        
                elif field.field_type == 'date':
                    try:
                        datetime.strptime(value, '%Y-%m-%d')
                    except ValueError:
                        errors.append({"error": "Value must be a valid date in YYYY-MM-DD format", "item": item})
                        continue
                        
                elif field.field_type == 'select' and field.options:
                    if value not in field.options:
                        errors.append({"error": f"Value must be one of: {', '.join(field.options)}", "item": item})
                        continue
                
                metadata = DocumentMetadata.objects.create(
                    document=document,
                    field=field,
                    value=value,
                    created_by=request.user
                )
                results.append({"id": metadata.id, "status": "created"})
                
            except CustomMetadataField.DoesNotExist:
                errors.append({"error": "Field not found", "item": item})
    
    return Response({
        "results": results,
        "errors": errors
    }, status=status.HTTP_200_OK if not errors else status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def signature_request_respond(request, pk):
    """Respond to a signature request (sign or decline)"""
    try:
        signature_request = DocumentSignatureRequest.objects.get(pk=pk)
    except DocumentSignatureRequest.DoesNotExist:
        return Response({"detail": "Signature request not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Validate status
    if 'status' not in request.data:
        return Response({"status": "This field is required"}, status=status.HTTP_400_BAD_REQUEST)
        
    if request.data['status'] not in ['signed', 'declined']:
        return Response({"status": "Status must be 'signed' or 'declined'"}, status=status.HTTP_400_BAD_REQUEST)
        
    # Validate decline reason
    if request.data['status'] == 'declined' and 'decline_reason' not in request.data:
        return Response({"decline_reason": "Decline reason is required when status is declined"}, status=status.HTTP_400_BAD_REQUEST)
        
    # Validate signature data
    if request.data['status'] == 'signed' and ('signature_data' not in request.data or not request.data['signature_data']):
        return Response({"signature_data": "Signature data is required when status is signed"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Update the signature request
    signature_request.status = request.data['status']
    signature_request.response_date = timezone.now()
    
    if request.data['status'] == 'declined':
        signature_request.decline_reason = request.data['decline_reason']
        signature_request.save()
        
        # Create notification for the requester
        create_signature_request_notification(signature_request)
        
        return Response({"detail": "Signature request declined"}, status=status.HTTP_200_OK)
    
    # Create signature if status is 'signed'
    if request.data['status'] == 'signed':
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
            
        # Generate verification hash
        data = f"{signature_request.document.id}:{signature_request.signer.id}:{time.time()}:{request.data['signature_data']}"
        verification_hash = hashlib.sha256(data.encode()).hexdigest()
        
        signature = DocumentSignature.objects.create(
            signature_request=signature_request,
            document=signature_request.document,
            signer=request.user,
            signature_type='electronic',
            signature_data=request.data['signature_data'],
            signature_date=timezone.now(),
            ip_address=ip,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            verification_hash=verification_hash
        )
        signature_request.save()
        
        # Create notification for the requester
        create_signature_request_notification(signature_request)
        
        return Response({"detail": "Document signed successfully"}, status=status.HTTP_200_OK)
    
    return Response({"detail": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
