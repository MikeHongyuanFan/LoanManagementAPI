from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from documents.models import Document, DocumentApproval, DocumentSignatureRequest
from django.utils import timezone
import datetime

User = get_user_model()

class ApprovalSignatureValidationTestCase(TestCase):
    """Test case for document approval and signature input validation."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.reviewer = User.objects.create_user(
            username='reviewer',
            email='reviewer@example.com',
            password='reviewerpassword'
        )
        self.signer = User.objects.create_user(
            username='signer',
            email='signer@example.com',
            password='signerpassword'
        )
        self.document = Document.objects.create(
            title='Test Document',
            description='Test document description',
            document_type='other',
            uploaded_by=self.user
        )
        self.approval = DocumentApproval.objects.create(
            document=self.document,
            reviewer=self.reviewer,
            requested_by=self.user,
            status='pending',
            requested_date=timezone.now()
        )
        self.signature_request = DocumentSignatureRequest.objects.create(
            document=self.document,
            signer=self.signer,
            requested_by=self.user,
            status='pending',
            requested_date=timezone.now()
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_approval_missing_required_fields(self):
        """Test that creating an approval without required fields returns 400."""
        data = {
            # Missing required 'reviewer_id' field
            'document': self.document.id,
            'status': 'pending'
        }
        response = self.client.post(f'/api/document-management/documents/{self.document.id}/request-approval/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('reviewer_id', response.data)
    
    def test_create_approval_invalid_status(self):
        """Test that creating an approval with invalid status returns 400."""
        data = {
            'document': self.document.id,
            'reviewer_id': self.reviewer.id,
            'status': 'invalid_status'  # Invalid status
        }
        response = self.client.post('/api/document-management/approvals/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('status', response.data)
    
    def test_create_approval_invalid_document(self):
        """Test that creating an approval with invalid document returns 400."""
        data = {
            'reviewer_id': self.reviewer.id,
            'approval_level': 1
        }
        response = self.client.post('/api/document-management/documents/999/request-approval/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_create_approval_invalid_reviewer(self):
        """Test that creating an approval with invalid reviewer returns 400."""
        data = {
            'reviewer_id': 999,  # Non-existent reviewer
            'approval_level': 1
        }
        response = self.client.post(f'/api/document-management/documents/{self.document.id}/request-approval/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('reviewer_id', response.data)
    
    def test_update_approval_invalid_data(self):
        """Test that updating an approval with invalid data returns 400."""
        data = {
            'status': 'invalid_status'  # Invalid status
        }
        response = self.client.patch(f'/api/document-management/approvals/{self.approval.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('status', response.data)
    
    def test_respond_to_approval_invalid_data(self):
        """Test that responding to an approval with invalid data returns 400."""
        self.client.force_authenticate(user=self.reviewer)
        data = {
            'status': 'invalid_status',  # Invalid status
            'comments': 'Test comments'
        }
        response = self.client.post(f'/api/document-management/approvals/{self.approval.id}/respond/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('status', response.data)
    
    def test_create_signature_request_missing_required_fields(self):
        """Test that creating a signature request without required fields returns 400."""
        data = {
            # Missing required 'signer_id' field
            'document': self.document.id,
            'message': 'Please sign this document'
        }
        response = self.client.post('/api/document-management/signature-requests/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('signer_id', response.data)
    
    def test_create_signature_request_invalid_document(self):
        """Test that creating a signature request with invalid document returns 400."""
        data = {
            'document': 999,  # Non-existent document
            'signer_id': self.signer.id,
            'message': 'Please sign this document'
        }
        response = self.client.post('/api/document-management/signature-requests/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_signature_request_invalid_signer(self):
        """Test that creating a signature request with invalid signer returns 400."""
        data = {
            'document': self.document.id,
            'signer_id': 999,  # Non-existent signer
            'message': 'Please sign this document'
        }
        response = self.client.post('/api/document-management/signature-requests/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('signer_id', response.data)
    
    def test_create_signature_request_invalid_due_date(self):
        """Test that creating a signature request with invalid due date returns 400."""
        data = {
            'document': self.document.id,
            'signer_id': self.signer.id,
            'message': 'Please sign this document',
            'due_date': 'invalid-date'  # Invalid date format
        }
        response = self.client.post('/api/document-management/signature-requests/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_signature_request_invalid_data(self):
        """Test that updating a signature request with invalid data returns 400."""
        data = {
            'status': 'invalid_status'  # Invalid status
        }
        response = self.client.patch(f'/api/document-management/signature-requests/{self.signature_request.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_respond_to_signature_request_invalid_data(self):
        """Test that responding to a signature request with invalid data returns 400."""
        self.client.force_authenticate(user=self.signer)
        data = {
            'status': 'invalid_status',  # Invalid status
            'signature_data': 'Test signature data'
        }
        response = self.client.post(f'/api/document-management/signature-requests/{self.signature_request.id}/respond/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_decline_signature_request_missing_reason(self):
        """Test that declining a signature request without a reason returns 400."""
        self.client.force_authenticate(user=self.signer)
        data = {
            'status': 'declined',
            # Missing required 'decline_reason' field when status is 'declined'
        }
        response = self.client.post(f'/api/document-management/signature-requests/{self.signature_request.id}/respond/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('decline_reason', response.data)
    
    def test_sign_document_invalid_signature_data(self):
        """Test that signing a document with invalid signature data returns 400."""
        self.client.force_authenticate(user=self.signer)
        data = {
            'status': 'signed',
            'signature_data': ''  # Empty signature data
        }
        response = self.client.post(f'/api/document-management/signature-requests/{self.signature_request.id}/respond/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('signature_data', response.data)
