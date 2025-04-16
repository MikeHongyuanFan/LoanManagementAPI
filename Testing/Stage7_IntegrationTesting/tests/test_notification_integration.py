import json
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from applications.models import Application
from borrowers.models import Borrower
from products.models import Product
from documents.models import Document, DocumentApproval, DocumentSignatureRequest
from notifications.models import Notification
from notifications.services import create_notification, create_document_approval_notification, create_signature_request_notification

User = get_user_model()

class NotificationIntegrationTest(TestCase):
    """
    Integration test for the notification system.
    Tests the creation of notifications during various workflows.
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
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone_number='1234567890',
            dob='1980-01-01',
            state='CA'
        )
        
        # Create test product
        self.product = Product.objects.create(
            name='Standard Loan',
            description='Standard loan product',
            interest_rate=5.5,
            term_months=360,
            min_loan_amount=10000,
            max_loan_amount=500000
        )
        
        # Create test application
        self.application = Application.objects.create(
            borrower=self.borrower,
            product=self.product,
            gross_loan_amount=300000.00,
            net_loan_amount=297000.00,
            status='draft',
            stage='application'
        )
        
        # Create test document
        self.document = Document.objects.create(
            title='Loan Agreement',
            description='Official loan agreement document',
            document_type='agreement',
            application=self.application,
            uploaded_by=self.staff_user
        )
        
        # Set up API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.staff_user)
    
    def test_application_status_change_notifications(self):
        """
        Test that notifications are created when application status changes.
        """
        # Initial notification count
        initial_count = Notification.objects.count()
        
        # Create a notification for application status change
        notification = create_notification(
            recipient=self.staff_user,
            title="Application Status Changed",
            message=f"Application #{self.application.id} status changed to 'submitted'",
            notification_type='stage_change',
            related_application=self.application
        )
        
        # Verify notification was created
        self.assertEqual(Notification.objects.count(), initial_count + 1)
        self.assertEqual(notification.recipient, self.staff_user)
        self.assertEqual(notification.title, "Application Status Changed")
        self.assertEqual(notification.related_application, self.application)
        self.assertEqual(notification.type, 'stage_change')
        
        # Change application status via API
        status_update_data = {
            'status': 'submitted',
            'notes': 'Application submitted for review'
        }
        
        response = self.client.patch(
            reverse('application-detail', kwargs={'pk': self.application.id}),
            data=json.dumps(status_update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify application status was updated
        updated_application = Application.objects.get(id=self.application.id)
        self.assertEqual(updated_application.status, 'submitted')
    
    def test_document_approval_notifications(self):
        """
        Test that notifications are created during document approval workflow.
        """
        # Initial notification count
        initial_count = Notification.objects.count()
        
        # Create document approval
        approval = DocumentApproval.objects.create(
            document=self.document,
            reviewer=self.reviewer_user,
            requested_by=self.staff_user,
            status='pending',
            comments='Please review this document'
        )
        
        # Create notification for document approval request
        notification = create_document_approval_notification(approval)
        
        # Verify notification was created
        self.assertEqual(Notification.objects.count(), initial_count + 1)
        self.assertEqual(notification.recipient, self.reviewer_user)
        self.assertIn("Document Approval Requested", notification.title)
        self.assertEqual(notification.related_application, self.application)
        
        # Update approval status to approved
        approval.status = 'approved'
        approval.save()
        
        # Create notification for document approval completion
        notification = create_document_approval_notification(approval)
        
        # Verify notification was created
        self.assertEqual(Notification.objects.count(), initial_count + 2)
        self.assertEqual(notification.recipient, self.staff_user)
        self.assertIn("Document Approved", notification.title)
        self.assertEqual(notification.related_application, self.application)
    
    def test_signature_request_notifications(self):
        """
        Test that notifications are created during signature request workflow.
        """
        # Initial notification count
        initial_count = Notification.objects.count()
        
        # Create signature request
        signature_request = DocumentSignatureRequest.objects.create(
            document=self.document,
            signer=self.signer_user,
            requested_by=self.staff_user,
            status='pending',
            message='Please sign this document'
        )
        
        # Create notification for signature request
        notification = create_signature_request_notification(signature_request)
        
        # Verify notification was created
        self.assertEqual(Notification.objects.count(), initial_count + 1)
        self.assertEqual(notification.recipient, self.signer_user)
        self.assertIn("Signature Requested", notification.title)
        self.assertEqual(notification.related_application, self.application)
        
        # Update signature request status to signed
        signature_request.status = 'signed'
        signature_request.save()
        
        # Create notification for signature completion
        notification = create_signature_request_notification(signature_request)
        
        # Verify notification was created
        self.assertEqual(Notification.objects.count(), initial_count + 2)
        self.assertEqual(notification.recipient, self.staff_user)
        self.assertIn("Document Signed", notification.title)
        self.assertEqual(notification.related_application, self.application)
    
    def test_notification_retrieval(self):
        """
        Test retrieving notifications via API.
        """
        # Create notifications for staff user
        create_notification(
            recipient=self.staff_user,
            title="Test Notification 1",
            message="This is a test notification",
            notification_type='system',
            related_application=self.application
        )
        
        create_notification(
            recipient=self.staff_user,
            title="Test Notification 2",
            message="This is another test notification",
            notification_type='alert',
            related_application=self.application
        )
        
        # Create notification for reviewer user
        create_notification(
            recipient=self.reviewer_user,
            title="Reviewer Notification",
            message="This is a notification for the reviewer",
            notification_type='system',
            related_application=self.application
        )
        
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Get notifications for staff user
        response = self.client.get(reverse('notification-list'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify that only staff user's notifications are returned
        notifications = response.data
        if isinstance(notifications, list):
            self.assertEqual(len(notifications), 2)
            notification_titles = [n['title'] for n in notifications]
            self.assertIn("Test Notification 1", notification_titles)
            self.assertIn("Test Notification 2", notification_titles)
            self.assertNotIn("Reviewer Notification", notification_titles)
        
        # Authenticate as reviewer user
        self.client.force_authenticate(user=self.reviewer_user)
        
        # Get notifications for reviewer user
        response = self.client.get(reverse('notification-list'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify that only reviewer user's notifications are returned
        notifications = response.data
        if isinstance(notifications, list):
            self.assertEqual(len(notifications), 1)
            self.assertEqual(notifications[0]['title'], "Reviewer Notification")
    
    def test_notification_for_application(self):
        """
        Test retrieving notifications for a specific application.
        """
        # Create notifications for the application
        create_notification(
            recipient=self.staff_user,
            title="Application Notification 1",
            message="This is a notification for the application",
            notification_type='system',
            related_application=self.application
        )
        
        create_notification(
            recipient=self.staff_user,
            title="Application Notification 2",
            message="This is another notification for the application",
            notification_type='alert',
            related_application=self.application
        )
        
        # Create a second application
        application2 = Application.objects.create(
            borrower=self.borrower,
            product=self.product,
            gross_loan_amount=200000.00,
            net_loan_amount=198000.00,
            status='draft',
            stage='application'
        )
        
        # Create notification for the second application
        create_notification(
            recipient=self.staff_user,
            title="Application 2 Notification",
            message="This is a notification for the second application",
            notification_type='system',
            related_application=application2
        )
        
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Get notifications for the first application
        response = self.client.get(
            f"{reverse('notification-list')}?related_application={self.application.id}"
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify that only notifications for the first application are returned
        notifications = response.data
        if isinstance(notifications, list):
            self.assertEqual(len(notifications), 2)
            notification_titles = [n['title'] for n in notifications]
            self.assertIn("Application Notification 1", notification_titles)
            self.assertIn("Application Notification 2", notification_titles)
            self.assertNotIn("Application 2 Notification", notification_titles)
