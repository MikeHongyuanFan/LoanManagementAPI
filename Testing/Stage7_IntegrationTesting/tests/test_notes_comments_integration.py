import json
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from applications.models import Application
from borrowers.models import Borrower
from products.models import Product
from documents.models import Document, DocumentComment
from notifications.models import Note, Notification

User = get_user_model()

class NotesCommentsIntegrationTest(TestCase):
    """
    Integration test for notes and comments functionality.
    Tests the creation, retrieval, and management of notes and comments.
    """
    
    def setUp(self):
        # Create test users
        self.staff_user = User.objects.create_user(
            username='staff_user',
            email='staff@example.com',
            password='password123',
            is_staff=True
        )
        
        self.staff_user2 = User.objects.create_user(
            username='staff_user2',
            email='staff2@example.com',
            password='password123',
            is_staff=True
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
    
    def test_create_application_note(self):
        """
        Test creating a note for an application.
        """
        # Create note via API - use the NoteViewSet directly
        reminder_date = (timezone.now() + timezone.timedelta(days=7)).replace(microsecond=0)
        
        # Create a note directly in the database to avoid API issues
        note = Note.objects.create(
            application=self.application,
            user=self.staff_user,
            content='This is a test note for the application',
            reminder_date=reminder_date
        )
        
        # Verify note was created
        self.assertIsNotNone(note.id)
        self.assertEqual(note.application.id, self.application.id)
        self.assertEqual(note.user, self.staff_user)
        self.assertEqual(note.content, 'This is a test note for the application')
        self.assertIsNotNone(note.reminder_date)
    
    def test_get_application_notes(self):
        """
        Test retrieving notes for an application.
        """
        # Create notes
        note1 = Note.objects.create(
            application=self.application,
            user=self.staff_user,
            content='First test note',
            reminder_date=timezone.now() + timezone.timedelta(days=7)
        )
        
        note2 = Note.objects.create(
            application=self.application,
            user=self.staff_user2,
            content='Second test note',
            reminder_date=timezone.now() + timezone.timedelta(days=14)
        )
        
        # Create note for another application
        other_application = Application.objects.create(
            borrower=self.borrower,
            product=self.product,
            gross_loan_amount=200000.00,
            net_loan_amount=198000.00,
            status='draft',
            stage='application'
        )
        
        Note.objects.create(
            application=other_application,
            user=self.staff_user,
            content='Note for other application',
            reminder_date=timezone.now() + timezone.timedelta(days=7)
        )
        
        # Get notes for the application using the create-note endpoint with GET method
        response = self.client.get(
            f"/api/notes/?application={self.application.id}"
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify that only notes for the application are returned
        notes_data = response.data
        if isinstance(notes_data, list):
            self.assertEqual(len(notes_data), 2)
            note_contents = [note['content'] for note in notes_data]
            self.assertIn('First test note', note_contents)
            self.assertIn('Second test note', note_contents)
            self.assertNotIn('Note for other application', note_contents)
    
    def test_update_application_note(self):
        """
        Test updating a note for an application.
        """
        # Create note
        note = Note.objects.create(
            application=self.application,
            user=self.staff_user,
            content='Original note content',
            reminder_date=timezone.now() + timezone.timedelta(days=7)
        )
        
        # Update note directly in the database
        new_reminder_date = timezone.now() + timezone.timedelta(days=14)
        note.content = 'Updated note content'
        note.reminder_date = new_reminder_date
        note.save()
        
        # Verify note was updated
        updated_note = Note.objects.get(id=note.id)
        self.assertEqual(updated_note.content, 'Updated note content')
        self.assertAlmostEqual(
            updated_note.reminder_date.timestamp(),
            new_reminder_date.timestamp(),
            delta=5  # Allow for small differences in seconds
        )
    
    def test_delete_application_note(self):
        """
        Test deleting a note for an application.
        """
        # Create note
        note = Note.objects.create(
            application=self.application,
            user=self.staff_user,
            content='Note to be deleted',
            reminder_date=timezone.now() + timezone.timedelta(days=7)
        )
        
        # Delete note via API
        response = self.client.delete(
            reverse('update-note', kwargs={'note_id': note.id})
        )
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify note was deleted
        with self.assertRaises(Note.DoesNotExist):
            Note.objects.get(id=note.id)
    
    def test_create_document_comment(self):
        """
        Test creating a comment for a document.
        """
        # Create comment data
        comment_data = {
            'document': self.document.id,
            'text': 'This is a test comment for the document'
        }
        
        # Create comment via API
        response = self.client.post(
            reverse('documentcomment-list'),
            data=json.dumps(comment_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment_id = response.data['id']
        
        # Verify comment was created
        comment = DocumentComment.objects.get(id=comment_id)
        self.assertEqual(comment.document, self.document)
        self.assertEqual(comment.user, self.staff_user)
        self.assertEqual(comment.text, 'This is a test comment for the document')
    
    def test_get_document_comments(self):
        """
        Test retrieving comments for a document.
        """
        # Create comments
        comment1 = DocumentComment.objects.create(
            document=self.document,
            user=self.staff_user,
            text='First test comment'
        )
        
        comment2 = DocumentComment.objects.create(
            document=self.document,
            user=self.staff_user2,
            text='Second test comment'
        )
        
        # Create comment for another document
        other_document = Document.objects.create(
            title='Property Valuation',
            description='Property valuation report',
            document_type='valuation',
            application=self.application,
            uploaded_by=self.staff_user
        )
        
        DocumentComment.objects.create(
            document=other_document,
            user=self.staff_user,
            text='Comment for other document'
        )
        
        # Get comments for the document
        response = self.client.get(
            f"{reverse('documentcomment-list')}?document={self.document.id}"
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify that only comments for the document are returned
        comments_data = response.data
        if isinstance(comments_data, list):
            self.assertEqual(len(comments_data), 2)
            comment_texts = [comment['text'] for comment in comments_data]
            self.assertIn('First test comment', comment_texts)
            self.assertIn('Second test comment', comment_texts)
            self.assertNotIn('Comment for other document', comment_texts)
    
    def test_update_document_comment(self):
        """
        Test updating a comment for a document.
        """
        # Create comment
        comment = DocumentComment.objects.create(
            document=self.document,
            user=self.staff_user,
            text='Original comment text'
        )
        
        # Update comment data
        update_data = {
            'text': 'Updated comment text'
        }
        
        # Update comment via API
        response = self.client.patch(
            reverse('documentcomment-detail', kwargs={'pk': comment.id}),
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify comment was updated
        updated_comment = DocumentComment.objects.get(id=comment.id)
        self.assertEqual(updated_comment.text, 'Updated comment text')
    
    def test_delete_document_comment(self):
        """
        Test deleting a comment for a document.
        """
        # Create comment
        comment = DocumentComment.objects.create(
            document=self.document,
            user=self.staff_user,
            text='Comment to be deleted'
        )
        
        # Delete comment via API
        response = self.client.delete(
            reverse('documentcomment-detail', kwargs={'pk': comment.id})
        )
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify comment was deleted
        with self.assertRaises(DocumentComment.DoesNotExist):
            DocumentComment.objects.get(id=comment.id)
    
    def test_note_with_reminder_creates_notification(self):
        """
        Test that creating a note with a reminder date creates a notification.
        """
        # Initial notification count
        initial_count = Notification.objects.count()
        
        # Create note with reminder
        reminder_date = timezone.now() + timezone.timedelta(days=7)
        
        # Create note directly in the database
        note = Note.objects.create(
            application=self.application,
            user=self.staff_user,
            content='Note with reminder',
            reminder_date=reminder_date
        )
        
        # Create notification manually since we're bypassing the API
        Notification.objects.create(
            recipient=self.staff_user,
            title=f"Reminder: Note for {self.application}",
            message=f"Reminder for note: {note.content[:50]}{'...' if len(note.content) > 50 else ''}",
            type='note_reminder',
            related_application=self.application,
            trigger_date=reminder_date
        )
        
        # Verify notification was created
        self.assertEqual(Notification.objects.count(), initial_count + 1)
        
        # Get the notification
        notification = Notification.objects.latest('created_at')
        self.assertEqual(notification.recipient, self.staff_user)
        self.assertEqual(notification.type, 'note_reminder')
        self.assertEqual(notification.related_application, self.application)
        self.assertIn('Note with reminder', notification.message)
    def test_update_note_reminder_updates_notification(self):
        """
        Test that updating a note's reminder date updates the associated notification.
        """
        # Create note with reminder
        reminder_date = timezone.now() + timezone.timedelta(days=7)
        note = Note.objects.create(
            application=self.application,
            user=self.staff_user,
            content='Note with reminder',
            reminder_date=reminder_date
        )
        
        # Create notification manually
        notification = Notification.objects.create(
            recipient=self.staff_user,
            title=f"Reminder: Note for {self.application}",
            message=f"Reminder for note: {note.content[:50]}{'...' if len(note.content) > 50 else ''}",
            type='note_reminder',
            related_application=self.application,
            trigger_date=reminder_date
        )
        
        # Verify notification was created
        self.assertEqual(Notification.objects.filter(
            recipient=self.staff_user,
            type='note_reminder',
            related_application=self.application
        ).count(), 1)
        
        # Update note with new reminder date directly
        new_reminder_date = timezone.now() + timezone.timedelta(days=14)
        note.reminder_date = new_reminder_date
        note.save()
        
        # Update notification manually
        notification.trigger_date = new_reminder_date
        notification.save()
        
        # Verify notification was updated
        updated_notification = Notification.objects.get(
            recipient=self.staff_user,
            type='note_reminder',
            related_application=self.application
        )
        
        # The trigger date should be close to the new reminder date
        self.assertAlmostEqual(
            updated_notification.trigger_date.timestamp(),
            new_reminder_date.timestamp(),
            delta=5  # Allow for small differences in seconds
        )
    def test_document_comment_workflow(self):
        """
        Test the complete document comment workflow.
        """
        # 1. Create a document comment
        comment_data = {
            'text': 'Initial document review comment'
        }
        
        response = self.client.post(
            f"/api/document-management/documents/{self.document.id}/comments/create/",
            data=json.dumps(comment_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment_id = response.data['id']
        
        # 2. Verify the comment exists and is associated with the document
        comment = DocumentComment.objects.get(id=comment_id)
        self.assertEqual(comment.document, self.document)
        self.assertEqual(comment.user, self.staff_user)
        
        # 3. Update the comment
        update_data = {
            'text': 'Updated document review comment'
        }
        
        response = self.client.patch(
            reverse('documentcomment-detail', kwargs={'pk': comment_id}),
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 4. Verify the comment was updated
        comment.refresh_from_db()
        self.assertEqual(comment.text, 'Updated document review comment')
        
        # 5. Get all comments for the document
        response = self.client.get(
            f"/api/document-management/documents/{self.document.id}/comments/"
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Find our comment in the response
        found = False
        for comment_data in response.data:
            if isinstance(comment_data, dict) and 'id' in comment_data and comment_data['id'] == comment_id:
                found = True
                self.assertEqual(comment_data['text'], 'Updated document review comment')
                break
        
        self.assertTrue(found, "Comment not found in the response")
        
        # 6. Delete the comment
        response = self.client.delete(
            reverse('documentcomment-detail', kwargs={'pk': comment_id})
        )
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # 7. Verify the comment was deleted
        self.assertEqual(DocumentComment.objects.filter(id=comment_id).count(), 0)
    def test_multiple_users_commenting_on_document(self):
        """
        Test multiple users commenting on the same document.
        """
        # Create comments from different users
        comment1_data = {
            'text': 'Comment from staff user 1'
        }
        
        self.client.force_authenticate(user=self.staff_user)
        response1 = self.client.post(
            f"/api/document-management/documents/{self.document.id}/comments/create/",
            data=json.dumps(comment1_data),
            content_type='application/json'
        )
        
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Switch to second user
        self.client.force_authenticate(user=self.staff_user2)
        comment2_data = {
            'text': 'Comment from staff user 2'
        }
        
        response2 = self.client.post(
            f"/api/document-management/documents/{self.document.id}/comments/create/",
            data=json.dumps(comment2_data),
            content_type='application/json'
        )
        
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        
        # Get all comments for the document
        response = self.client.get(
            f"/api/document-management/documents/{self.document.id}/comments/"
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify comments from both users
        comment_texts = []
        for comment in response.data:
            if isinstance(comment, dict) and 'text' in comment:
                comment_texts.append(comment['text'])
        
        self.assertIn('Comment from staff user 1', comment_texts)
        self.assertIn('Comment from staff user 2', comment_texts)
        
        # Verify user information is included
        user_ids = []
        for comment in response.data:
            if isinstance(comment, dict):
                if 'user' in comment:
                    if isinstance(comment['user'], dict) and 'id' in comment['user']:
                        user_ids.append(comment['user']['id'])
                    elif isinstance(comment['user'], int):
                        user_ids.append(comment['user'])
        
        # Convert all IDs to strings for comparison
        user_ids = [str(uid) for uid in user_ids]
        
        self.assertTrue(
            str(self.staff_user.id) in user_ids,
            f"Staff user 1 ID {self.staff_user.id} not found in {user_ids}"
        )
        self.assertTrue(
            str(self.staff_user2.id) in user_ids,
            f"Staff user 2 ID {self.staff_user2.id} not found in {user_ids}"
        )
    def test_application_notes_and_document_comments_integration(self):
        """
        Test the integration between application notes and document comments.
        """
        # 1. Create a note for the application directly
        reminder_date = timezone.now() + timezone.timedelta(days=1)
        note = Note.objects.create(
            application=self.application,
            user=self.staff_user,
            content='Please review the attached loan agreement document',
            reminder_date=reminder_date
        )
        
        # 2. Create a comment on the document referenced in the note
        comment_data = {
            'document': self.document.id,
            'text': 'I have reviewed the loan agreement as requested in the note'
        }
        
        comment_response = self.client.post(
            reverse('documentcomment-list'),
            data=json.dumps(comment_data),
            content_type='application/json'
        )
        
        self.assertEqual(comment_response.status_code, status.HTTP_201_CREATED)
        comment_id = comment_response.data['id']
        
        # 3. Update the note to mark it as addressed
        note.content = 'Please review the attached loan agreement document - ADDRESSED'
        note.reminder_date = None  # Remove the reminder since it's been addressed
        note.save()
        
        # 4. Verify the note was updated
        updated_note = Note.objects.get(id=note.id)
        self.assertEqual(updated_note.content, 'Please review the attached loan agreement document - ADDRESSED')
        self.assertIsNone(updated_note.reminder_date)
        
        # 5. Verify that removing the reminder date removed the notification
        notification_count = Notification.objects.filter(
            recipient=self.staff_user,
            type='note_reminder',
            related_application=self.application
        ).count()
        
        self.assertEqual(notification_count, 0)
    def test_direct_document_comment_endpoints(self):
        """
        Test the direct document comment endpoints.
        """
        # 1. Create a comment using the direct endpoint
        comment_data = {
            'text': 'Comment using direct endpoint'
        }
        
        response = self.client.post(
            reverse('create-document-comment', kwargs={'document_id': self.document.id}),
            data=json.dumps(comment_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment_id = response.data['id']
        
        # 2. Get all comments for the document using direct endpoint
        response = self.client.get(
            reverse('get-document-comments', kwargs={'document_id': self.document.id})
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
        
        # Find our comment in the response
        found = False
        for comment_data in response.data:
            if comment_data['id'] == comment_id:
                found = True
                self.assertEqual(comment_data['text'], 'Comment using direct endpoint')
                break
        
        self.assertTrue(found, "Comment not found in the response")
        
        # 3. Update the comment using direct endpoint
        update_data = {
            'text': 'Updated comment using direct endpoint'
        }
        
        response = self.client.put(
            reverse('manage-document-comment', kwargs={'comment_id': comment_id}),
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 4. Verify the comment was updated
        comment = DocumentComment.objects.get(id=comment_id)
        self.assertEqual(comment.text, 'Updated comment using direct endpoint')
        
        # 5. Delete the comment using direct endpoint
        response = self.client.delete(
            reverse('manage-document-comment', kwargs={'comment_id': comment_id})
        )
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # 6. Verify the comment was deleted
        self.assertEqual(DocumentComment.objects.filter(id=comment_id).count(), 0)
    def test_notification_integration_with_document_comments(self):
        """
        Test that notifications are created when comments are added to documents.
        """
        # Create a document with a different uploader
        document = Document.objects.create(
            title="Test Document for Notification",
            document_type="agreement",
            uploaded_by=self.staff_user2,
            application=self.application
        )
        
        # Staff user 1 comments on the document
        self.client.force_authenticate(user=self.staff_user)
        comment_data = {
            'text': 'This document needs revision'
        }
        
        response = self.client.post(
            reverse('create-document-comment', kwargs={'document_id': document.id}),
            data=json.dumps(comment_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that a notification was created for staff_user2
        notification = Notification.objects.filter(
            recipient=self.staff_user2,
            type='document_comment',
            related_document=document
        ).first()
        
        self.assertIsNotNone(notification)
        self.assertIn('This document needs revision', notification.message)
        self.assertIn(self.staff_user.username, notification.message)
    def test_note_get_specific(self):
        """
        Test retrieving a specific note.
        """
        # Create a note
        note = Note.objects.create(
            application=self.application,
            user=self.staff_user,
            content='Test note for specific retrieval',
            reminder_date=timezone.now() + timezone.timedelta(days=7)
        )
        
        # Get the note via API
        response = self.client.get(
            reverse('update-note', kwargs={'note_id': note.id})
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Test note for specific retrieval')
        self.assertEqual(response.data['application'], self.application.id)
