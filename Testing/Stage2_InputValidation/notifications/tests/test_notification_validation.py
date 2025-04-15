from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from notifications.models import Notification

User = get_user_model()

class NotificationValidationTestCase(TestCase):
    """Test case for notification input validation."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.notification = Notification.objects.create(
            recipient=self.user,
            title='Test Notification',
            message='This is a test notification',
            type='system',
            sent_status=False
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_notification_missing_required_fields(self):
        """Test that creating a notification without required fields returns 400."""
        data = {
            # Missing required 'recipient' field
            'title': 'Test Notification',
            'message': 'This is a test notification',
            'type': 'system',
            'sent_status': False
        }
        response = self.client.post('/api/notifications/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('recipient', response.data)
    
    def test_create_notification_invalid_type(self):
        """Test that creating a notification with invalid type returns 400."""
        data = {
            'recipient': self.user.id,
            'title': 'Test Notification',
            'message': 'This is a test notification',
            'type': 'invalid_type',  # Invalid type
            'sent_status': False
        }
        response = self.client.post('/api/notifications/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('type', response.data)
    
    def test_create_notification_title_too_long(self):
        """Test that creating a notification with a title that's too long returns 400."""
        data = {
            'recipient': self.user.id,
            'title': 'T' * 256,  # 256 characters, but max is 255
            'message': 'This is a test notification',
            'type': 'system',
            'sent_status': False
        }
        response = self.client.post('/api/notifications/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
    
    def test_update_notification_invalid_data(self):
        """Test that updating a notification with invalid data returns 400."""
        data = {
            'type': 'invalid_type'  # Invalid type
        }
        response = self.client.patch(f'/api/notifications/{self.notification.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('type', response.data)
    
    def test_filter_notifications_invalid_parameters(self):
        """Test that filtering notifications with invalid parameters returns appropriate response."""
        response = self.client.get('/api/notifications/?type=invalid_type')  # Invalid type
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('type', response.data)
        
        response = self.client.get('/api/notifications/?created_after=invalid-date')  # Invalid date format
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('created_after', response.data)
