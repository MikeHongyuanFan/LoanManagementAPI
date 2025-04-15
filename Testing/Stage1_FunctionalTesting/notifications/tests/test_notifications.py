from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from notifications.models import Notification
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class NotificationAPITestCase(TestCase):
    """Test case for the notification API endpoints."""
    
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
        
    def test_list_notifications(self):
        """Test that the notifications list endpoint returns 200 and correct data structure."""
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)
        
    def test_retrieve_notification(self):
        """Test that the notification detail endpoint returns 200 and correct data."""
        response = self.client.get(f'/api/notifications/{self.notification.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Notification')
        self.assertEqual(response.data['message'], 'This is a test notification')
        self.assertEqual(response.data['type'], 'system')
        self.assertEqual(response.data['sent_status'], False)
        
    def test_create_notification(self):
        """Test that creating a notification works correctly."""
        data = {
            'recipient': self.user.id,
            'title': 'New Notification',
            'message': 'This is a new notification',
            'type': 'email',
            'sent_status': False
        }
        response = self.client.post('/api/notifications/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Notification')
        self.assertEqual(response.data['type'], 'email')
        self.assertEqual(Notification.objects.count(), 2)
        
    def test_mark_notification_as_read(self):
        """Test that marking a notification as read works correctly."""
        data = {
            'sent_status': True
        }
        response = self.client.patch(f'/api/notifications/{self.notification.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['sent_status'], True)
        self.notification.refresh_from_db()
        self.assertEqual(self.notification.sent_status, True)
        
    def test_delete_notification(self):
        """Test that deleting a notification works correctly."""
        response = self.client.delete(f'/api/notifications/{self.notification.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Notification.objects.count(), 0)
        
    def test_filter_notifications_by_type(self):
        """Test that filtering notifications by type works correctly."""
        # Create additional notifications with different types
        Notification.objects.create(
            recipient=self.user,
            title='Email Notification',
            message='This is an email notification',
            type='email',
            sent_status=False
        )
        Notification.objects.create(
            recipient=self.user,
            title='Alert Notification',
            message='This is an alert notification',
            type='alert',
            sent_status=False
        )
        
        # Filter by system type
        response = self.client.get('/api/notifications/?type=system')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Notification')
        
        # Filter by email type
        response = self.client.get('/api/notifications/?type=email')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Email Notification')
        
    def test_filter_notifications_by_read_status(self):
        """Test that filtering notifications by read status works correctly."""
        # Create a read notification
        Notification.objects.create(
            recipient=self.user,
            title='Read Notification',
            message='This notification is already read',
            type='system',
            sent_status=True
        )
        
        # Filter by unread status
        response = self.client.get('/api/notifications/?sent_status=false')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Notification')
        
        # Filter by read status
        response = self.client.get('/api/notifications/?sent_status=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Read Notification')
