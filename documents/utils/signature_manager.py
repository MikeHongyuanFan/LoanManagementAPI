"""
Electronic signature management utilities
"""
import os
import uuid
import base64
import hashlib
import datetime
from io import BytesIO
from PIL import Image
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

from documents.models import Document, DocumentSignature, DocumentSignatureRequest

class SignatureManager:
    """Manager for electronic signature operations"""
    
    def __init__(self, user=None):
        """Initialize the signature manager
        
        Args:
            user: The user performing the signature operations
        """
        self.user = user
    
    def request_signature(self, document, signers, due_date=None, message=None):
        """Request signatures for a document
        
        Args:
            document: The document to be signed
            signers: List of users who need to sign the document
            due_date: Optional due date for signatures
            message: Optional message to include with the request
        
        Returns:
            List of signature requests
        """
        if document.status not in ['approved', 'signed']:
            raise ValidationError(f"Cannot request signatures for document with status '{document.status}'")
        
        # Set default due date if not provided (14 days from now)
        if not due_date:
            due_date = timezone.now() + datetime.timedelta(days=14)
        
        # Create signature requests
        with transaction.atomic():
            # Update document status
            if document.status != 'signed':
                document.status = 'pending_signature'
                document.save()
            
            # Create signature requests for each signer
            signature_requests = []
            
            for signer in signers:
                # Check if there's already an active request for this signer
                existing_request = DocumentSignatureRequest.objects.filter(
                    document=document,
                    signer=signer,
                    status__in=['pending', 'viewed']
                ).first()
                
                if existing_request:
                    # Update existing request
                    existing_request.due_date = due_date
                    existing_request.message = message or existing_request.message
                    existing_request.requested_by = self.user
                    existing_request.requested_date = timezone.now()
                    existing_request.status = 'pending'
                    existing_request.save()
                    signature_requests.append(existing_request)
                else:
                    # Create new request
                    signature_token = self._generate_signature_token()
                    
                    request = DocumentSignatureRequest.objects.create(
                        document=document,
                        signer=signer,
                        requested_by=self.user,
                        due_date=due_date,
                        message=message,
                        status='pending',
                        signature_token=signature_token
                    )
                    signature_requests.append(request)
            
            # Send notifications
            try:
                from documents.utils.notification_manager import DocumentNotificationManager
                notification_manager = DocumentNotificationManager(user=self.user)
                notification_manager.notify_signature_requested(document, signature_requests)
            except ImportError:
                # Notification system not available, continue without notifications
                pass
            
            return signature_requests
    
    def sign_document(self, signature_request, signature_data, signature_type='drawn'):
        """Sign a document
        
        Args:
            signature_request: The signature request to fulfill
            signature_data: The signature data (base64 encoded image for drawn signatures, text for typed)
            signature_type: Type of signature ('drawn', 'typed', 'digital')
        
        Returns:
            The created signature
        """
        if signature_request.status not in ['pending', 'viewed']:
            raise ValidationError(f"Cannot sign a request with status '{signature_request.status}'")
        
        document = signature_request.document
        
        with transaction.atomic():
            # Process signature data based on type
            if signature_type == 'drawn':
                # Process drawn signature (base64 encoded image)
                signature_image = self._process_signature_image(signature_data)
            else:
                # For typed or digital signatures, store as is
                signature_image = None
            
            # Create signature record
            signature = DocumentSignature.objects.create(
                document=document,
                signature_request=signature_request,
                signer=signature_request.signer,
                signature_type=signature_type,
                signature_data=signature_data if signature_type != 'drawn' else None,
                signature_date=timezone.now(),
                ip_address=self._get_client_ip(),
                user_agent=self._get_user_agent()
            )
            
            # Save signature image if available
            if signature_image:
                signature.signature_image.save(
                    f'signature_{signature.id}.png',
                    signature_image,
                    save=True
                )
            
            # Update signature request status
            signature_request.status = 'signed'
            signature_request.completed_date = timezone.now()
            signature_request.save()
            
            # Check if all signatures are complete
            pending_signatures = DocumentSignatureRequest.objects.filter(
                document=document,
                status__in=['pending', 'viewed']
            ).count()
            
            # If no pending signatures, update document status
            if pending_signatures == 0:
                document.status = 'signed'
                document.save()
                
                # Create a new version with signatures embedded
                try:
                    from documents.utils.version_manager import DocumentVersionManager
                    version_manager = DocumentVersionManager(user=self.user)
                    
                    # Create a new version with embedded signatures
                    signed_document = self._embed_signatures_in_document(document)
                    
                    if signed_document:
                        new_version = version_manager.create_new_version(
                            document,
                            file=signed_document,
                            version_notes="Signed version"
                        )
                        new_version.status = 'signed'
                        new_version.save()
                except ImportError:
                    # Version manager not available, continue without creating new version
                    pass
            
            # Send notifications
            try:
                from documents.utils.notification_manager import DocumentNotificationManager
                notification_manager = DocumentNotificationManager(user=self.user)
                notification_manager.notify_document_signed(signature)
            except ImportError:
                # Notification system not available, continue without notifications
                pass
            
            return signature
    
    def decline_signature(self, signature_request, reason=None):
        """Decline to sign a document
        
        Args:
            signature_request: The signature request to decline
            reason: Reason for declining
        
        Returns:
            The updated signature request
        """
        if signature_request.status not in ['pending', 'viewed']:
            raise ValidationError(f"Cannot decline a request with status '{signature_request.status}'")
        
        document = signature_request.document
        
        with transaction.atomic():
            # Update signature request status
            signature_request.status = 'declined'
            signature_request.completed_date = timezone.now()
            signature_request.decline_reason = reason
            signature_request.save()
            
            # Update document status
            document.status = 'signature_declined'
            document.save()
            
            # Cancel other pending signature requests
            document.signature_requests.filter(status__in=['pending', 'viewed']).update(
                status='cancelled',
                completed_date=timezone.now()
            )
            
            # Send notifications
            try:
                from documents.utils.notification_manager import DocumentNotificationManager
                notification_manager = DocumentNotificationManager(user=self.user)
                notification_manager.notify_signature_declined(signature_request)
            except ImportError:
                # Notification system not available, continue without notifications
                pass
            
            return signature_request
    
    def cancel_signature_request(self, signature_request):
        """Cancel a signature request
        
        Args:
            signature_request: The signature request to cancel
        
        Returns:
            The updated signature request
        """
        if signature_request.status not in ['pending', 'viewed']:
            raise ValidationError(f"Cannot cancel a request with status '{signature_request.status}'")
        
        with transaction.atomic():
            # Update signature request status
            signature_request.status = 'cancelled'
            signature_request.completed_date = timezone.now()
            signature_request.save()
            
            # Check if all signature requests are cancelled
            document = signature_request.document
            active_requests = document.signature_requests.filter(
                status__in=['pending', 'viewed', 'signed']
            ).count()
            
            # If no active requests, update document status back to approved
            if active_requests == 0:
                document.status = 'approved'
                document.save()
            
            # Send notifications
            try:
                from documents.utils.notification_manager import DocumentNotificationManager
                notification_manager = DocumentNotificationManager(user=self.user)
                notification_manager.notify_signature_request_cancelled(signature_request)
            except ImportError:
                # Notification system not available, continue without notifications
                pass
            
            return signature_request
    
    def mark_request_as_viewed(self, signature_request):
        """Mark a signature request as viewed
        
        Args:
            signature_request: The signature request to mark as viewed
        
        Returns:
            The updated signature request
        """
        if signature_request.status != 'pending':
            return signature_request
        
        signature_request.status = 'viewed'
        signature_request.viewed_date = timezone.now()
        signature_request.save()
        
        return signature_request
    
    def get_signature_status(self, document):
        """Get signature status for a document
        
        Args:
            document: The document to check
        
        Returns:
            Dictionary with signature status information
        """
        # Get all signature requests for the document
        signature_requests = document.signature_requests.all()
        
        # Count requests by status
        total_requests = signature_requests.count()
        pending_requests = signature_requests.filter(status__in=['pending', 'viewed']).count()
        signed_requests = signature_requests.filter(status='signed').count()
        declined_requests = signature_requests.filter(status='declined').count()
        cancelled_requests = signature_requests.filter(status='cancelled').count()
        
        # Get signature history
        signature_history = []
        
        for request in signature_requests:
            history_item = {
                'id': request.id,
                'signer': {
                    'id': request.signer.id,
                    'name': request.signer.get_full_name() or request.signer.username,
                    'email': request.signer.email
                },
                'status': request.status,
                'requested_date': request.requested_date,
                'viewed_date': request.viewed_date,
                'completed_date': request.completed_date,
                'due_date': request.due_date
            }
            
            # Add signature information if signed
            if request.status == 'signed':
                signature = request.signature
                if signature:
                    history_item['signature'] = {
                        'id': signature.id,
                        'type': signature.signature_type,
                        'date': signature.signature_date
                    }
            
            # Add decline reason if declined
            if request.status == 'declined':
                history_item['decline_reason'] = request.decline_reason
            
            signature_history.append(history_item)
        
        return {
            'document_status': document.status,
            'total_requests': total_requests,
            'pending_requests': pending_requests,
            'signed_requests': signed_requests,
            'declined_requests': declined_requests,
            'cancelled_requests': cancelled_requests,
            'is_fully_signed': document.status == 'signed',
            'is_declined': document.status == 'signature_declined',
            'signature_history': signature_history
        }
    
    def verify_signature(self, signature):
        """Verify a signature's authenticity
        
        Args:
            signature: The signature to verify
        
        Returns:
            Dictionary with verification results
        """
        # Get signature metadata
        verification_data = {
            'signature_id': signature.id,
            'document_id': signature.document.id,
            'document_title': signature.document.title,
            'signer': {
                'id': signature.signer.id,
                'name': signature.signer.get_full_name() or signature.signer.username,
                'email': signature.signer.email
            },
            'signature_type': signature.signature_type,
            'signature_date': signature.signature_date,
            'ip_address': signature.ip_address,
            'user_agent': signature.user_agent,
            'is_valid': True
        }
        
        # Add verification hash
        verification_data['verification_hash'] = self._generate_verification_hash(signature)
        
        return verification_data
    
    def _process_signature_image(self, base64_data):
        """Process base64 encoded signature image
        
        Args:
            base64_data: Base64 encoded image data
        
        Returns:
            ContentFile with processed image
        """
        try:
            # Remove data URL prefix if present
            if ',' in base64_data:
                base64_data = base64_data.split(',')[1]
            
            # Decode base64 data
            image_data = base64.b64decode(base64_data)
            
            # Open image with PIL
            image = Image.open(BytesIO(image_data))
            
            # Convert to RGBA if not already
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # Create a white background
            background = Image.new('RGBA', image.size, (255, 255, 255, 255))
            
            # Composite the signature onto the background
            composite = Image.alpha_composite(background, image)
            
            # Convert back to RGB for better compatibility
            rgb_image = composite.convert('RGB')
            
            # Save to BytesIO
            output = BytesIO()
            rgb_image.save(output, format='PNG')
            output.seek(0)
            
            # Create ContentFile
            return ContentFile(output.read())
        except Exception as e:
            raise ValidationError(f"Invalid signature image data: {str(e)}")
    
    def _embed_signatures_in_document(self, document):
        """Embed signatures in document
        
        Args:
            document: The document to embed signatures in
        
        Returns:
            ContentFile with signed document or None if not supported
        """
        # This is a placeholder for actual signature embedding
        # In a real implementation, this would use a PDF library to embed signatures
        # For now, we'll just return the original document
        try:
            return document.file.open()
        except:
            return None
    
    def _generate_signature_token(self):
        """Generate a unique token for signature requests
        
        Returns:
            Unique signature token
        """
        return str(uuid.uuid4())
    
    def _generate_verification_hash(self, signature):
        """Generate a verification hash for a signature
        
        Args:
            signature: The signature to generate a hash for
        
        Returns:
            Verification hash
        """
        # Create a string with signature metadata
        verification_string = (
            f"{signature.id}|"
            f"{signature.document.id}|"
            f"{signature.signer.id}|"
            f"{signature.signature_date.isoformat()}|"
            f"{signature.ip_address or ''}|"
            f"{signature.signature_type}"
        )
        
        # Generate SHA-256 hash
        return hashlib.sha256(verification_string.encode()).hexdigest()
    
    def _get_client_ip(self):
        """Get client IP address
        
        Returns:
            Client IP address or None
        """
        # In a real implementation, this would get the IP from the request
        # For now, return a placeholder
        return "127.0.0.1"
    
    def _get_user_agent(self):
        """Get user agent string
        
        Returns:
            User agent string or None
        """
        # In a real implementation, this would get the user agent from the request
        # For now, return a placeholder
        return "Mozilla/5.0"
