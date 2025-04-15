import json
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from documents.models import Document, DocumentApproval, DocumentSignatureRequest, DocumentSignature
from applications.models import Application
from borrowers.models import Borrower
from notifications.models import Notification

User = get_user_model()

class DocumentWorkflowIntegrationTest(TestCase):
    """
    Integration test for document management workflows.
    Tests the interaction between documents, approvals, signatures, and notifications.
    """
    
    def setUp(self):
        # Create test users
        self.staff_user = User.objects.create_user(
            username='staff_user',
            email='staff@example.com',
            password='password123',
            is_staff=True
        )
        self.borrower_user = User.objects.create_user(
            username='borrower_user',
            email='borrower@example.com',
            password='password123'
        )
        self.reviewer_user = User.objects.create_user(
            username='reviewer_user',
            email='reviewer@example.com',
            password='password123',
            is_staff=True
        )
        self.signer_user = User.objects.create_user(
            username='signer_user',
            email='signer@example.com',
            password='password123'
        )
        
        # Create test borrower
        self.borrower = Borrower.objects.create(
            user=self.borrower_user,
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone_number='1234567890',
            date_of_birth='1980-01-01'
        )
        
        # Create test application
        self.application = Application.objects.create(
            borrower=self.borrower,
            loan_amount=300000.00,
            purpose='Home purchase',
            property_address='123 Main St, Anytown, USA',
            property_value=375000.00,
            status='in_progress'
        )
        
        # Create test document
        self.document = Document.objects.create(
            title='Loan Agreement',
            description='Official loan agreement document',
            document_type='agreement',
            application=self.application,
            created_by=self.staff_user
        )
        
        # Set up API client
        self.client = APIClient()
    
    def test_document_approval_signature_notification_workflow(self):
        """
        Test the complete document workflow including:
        1. Document approval request
        2. Approval notification
        3. Document approval
        4. Signature request
        5. Signature notification
        6. Document signing
        7. Final notification
        """
        # Step 1: Authenticate as staff and request document approval
        self.client.force_authenticate(user=self.staff_user)
        
        approval_data = {
            'document': self.document.id,
            'reviewer': self.reviewer_user.id,
            'comments': 'Please review this loan agreement'
        }
        
        response = self.client.post(
            reverse('document-request-approval', kwargs={'pk': self.document.id}),
            data=json.dumps(approval_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        approval_id = response.data['id']
        
        # Step 2: Verify approval notification was created
        reviewer_notifications = Notification.objects.filter(
            user=self.reviewer_user,
            notification_type='document_approval_request'
        )
        self.assertEqual(reviewer_notifications.count(), 1)
        self.assertIn(f'Document approval requested', reviewer_notifications.first().message)
        
        # Step 3: Authenticate as reviewer and approve document
        self.client.force_authenticate(user=self.reviewer_user)
        
        response = self.client.post(
            reverse('documentapproval-approve', kwargs={'pk': approval_id}),
            data=json.dumps({'comments': 'Document looks good'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 4: Verify approval notification was sent to requester
        requester_notifications = Notification.objects.filter(
            user=self.staff_user,
            notification_type='document_approved'
        )
        self.assertEqual(requester_notifications.count(), 1)
        self.assertIn(f'Document approved', requester_notifications.first().message)
        
        # Step 5: Authenticate as staff and request signature
        self.client.force_authenticate(user=self.staff_user)
        
        signature_data = {
            'document': self.document.id,
            'signer': self.signer_user.id,
            'message': 'Please sign this loan agreement'
        }
        
        response = self.client.post(
            reverse('document-request-signature', kwargs={'pk': self.document.id}),
            data=json.dumps(signature_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        signature_request_id = response.data['id']
        
        # Step 6: Verify signature notification was created
        signer_notifications = Notification.objects.filter(
            user=self.signer_user,
            notification_type='signature_requested'
        )
        self.assertEqual(signer_notifications.count(), 1)
        self.assertIn(f'Signature requested', signer_notifications.first().message)
        
        # Step 7: Authenticate as signer and sign document
        self.client.force_authenticate(user=self.signer_user)
        
        response = self.client.post(
            reverse('signature-request-respond', kwargs={'pk': signature_request_id}),
            data=json.dumps({
                'action': 'sign',
                'signature_data': 'base64_encoded_signature_data'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 8: Verify signature notification was sent to requester
        signature_notifications = Notification.objects.filter(
            user=self.staff_user,
            notification_type='document_signed'
        )
        self.assertEqual(signature_notifications.count(), 1)
        self.assertIn(f'Document signed', signature_notifications.first().message)
        
        # Step 9: Verify the final state of all components
        
        # Check document approval status
        approval = DocumentApproval.objects.get(document=self.document)
        self.assertEqual(approval.status, 'approved')
        self.assertEqual(approval.reviewer, self.reviewer_user)
        
        # Check signature request status
        signature_request = DocumentSignatureRequest.objects.get(document=self.document)
        self.assertEqual(signature_request.status, 'signed')
        self.assertEqual(signature_request.signer, self.signer_user)
        
        # Check signature exists
        signature = DocumentSignature.objects.get(signature_request=signature_request)
        self.assertIsNotNone(signature)
        self.assertEqual(signature.signed_by, self.signer_user)
        
        # Verify relationships between components
        self.assertEqual(approval.document, self.document)
        self.assertEqual(signature_request.document, self.document)
        self.assertEqual(signature.signature_request, signature_request)
        
        # Verify notifications were created with correct relationships
        self.assertEqual(reviewer_notifications.first().related_document, self.document)
        self.assertEqual(requester_notifications.first().related_document, self.document)
        self.assertEqual(signer_notifications.first().related_document, self.document)
        self.assertEqual(signature_notifications.first().related_document, self.document)
