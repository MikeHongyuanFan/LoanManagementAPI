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
            user=self.user,
            title='Test Notification',
            message='This is a test notification',
            notification_type='system',
            is_read=False
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
        self.assertEqual(response.data['notification_type'], 'system')
        self.assertEqual(response.data['is_read'], False)
        
    def test_create_notification(self):
        """Test that creating a notification works correctly."""
        data = {
            'user': self.user.id,
            'title': 'New Notification',
            'message': 'This is a new notification',
            'notification_type': 'email',
            'is_read': False
        }
        response = self.client.post('/api/notifications/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Notification')
        self.assertEqual(response.data['notification_type'], 'email')
        self.assertEqual(Notification.objects.count(), 2)
        
    def test_mark_notification_as_read(self):
        """Test that marking a notification as read works correctly."""
        data = {
            'is_read': True
        }
        response = self.client.patch(f'/api/notifications/{self.notification.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_read'], True)
        self.notification.refresh_from_db()
        self.assertEqual(self.notification.is_read, True)
        
    def test_delete_notification(self):
        """Test that deleting a notification works correctly."""
        response = self.client.delete(f'/api/notifications/{self.notification.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Notification.objects.count(), 0)
        
    def test_mark_all_as_read(self):
        """Test that marking all notifications as read works correctly."""
        # Create additional unread notifications
        Notification.objects.create(
            user=self.user,
            title='Second Notification',
            message='This is another test notification',
            notification_type='system',
            is_read=False
        )
        Notification.objects.create(
            user=self.user,
            title='Third Notification',
            message='This is yet another test notification',
            notification_type='email',
            is_read=False
        )
        
        response = self.client.post('/api/notifications/mark-all-read/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('marked_count', response.data)
        self.assertEqual(response.data['marked_count'], 3)
        
        # Verify all notifications are marked as read
        unread_count = Notification.objects.filter(user=self.user, is_read=False).count()
        self.assertEqual(unread_count, 0)
        
    def test_get_unread_count(self):
        """Test that getting unread notification count works correctly."""
        # Create additional unread notifications
        Notification.objects.create(
            user=self.user,
            title='Second Notification',
            message='This is another test notification',
            notification_type='system',
            is_read=False
        )
        # Create a read notification
        Notification.objects.create(
            user=self.user,
            title='Read Notification',
            message='This notification is already read',
            notification_type='email',
            is_read=True
        )
        
        response = self.client.get('/api/notifications/unread-count/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('unread_count', response.data)
        self.assertEqual(response.data['unread_count'], 2)
        
    def test_filter_notifications_by_type(self):
        """Test that filtering notifications by type works correctly."""
        # Create additional notifications with different types
        Notification.objects.create(
            user=self.user,
            title='Email Notification',
            message='This is an email notification',
            notification_type='email',
            is_read=False
        )
        Notification.objects.create(
            user=self.user,
            title='Alert Notification',
            message='This is an alert notification',
            notification_type='alert',
            is_read=False
        )
        
        # Filter by system type
        response = self.client.get('/api/notifications/?notification_type=system')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Notification')
        
        # Filter by email type
        response = self.client.get('/api/notifications/?notification_type=email')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Email Notification')
        
    def test_filter_notifications_by_read_status(self):
        """Test that filtering notifications by read status works correctly."""
        # Create a read notification
        Notification.objects.create(
            user=self.user,
            title='Read Notification',
            message='This notification is already read',
            notification_type='system',
            is_read=True
        )
        
        # Filter by unread status
        response = self.client.get('/api/notifications/?is_read=false')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Notification')
        
        # Filter by read status
        response = self.client.get('/api/notifications/?is_read=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Read Notification')
        
    def test_filter_notifications_by_date(self):
        """Test that filtering notifications by date works correctly."""
        # Create notifications with different dates
        yesterday = timezone.now() - timedelta(days=1)
        last_week = timezone.now() - timedelta(days=7)
        
        Notification.objects.create(
            user=self.user,
            title='Yesterday Notification',
            message='This notification is from yesterday',
            notification_type='system',
            is_read=False,
            created_at=yesterday
        )
        Notification.objects.create(
            user=self.user,
            title='Last Week Notification',
            message='This notification is from last week',
            notification_type='system',
            is_read=False,
            created_at=last_week
        )
        
        # Filter by date range
        yesterday_str = yesterday.strftime('%Y-%m-%d')
        response = self.client.get(f'/api/notifications/?created_after={yesterday_str}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)  # Today's and yesterday's
        
        # Filter by older date
        last_week_str = last_week.strftime('%Y-%m-%d')
        two_weeks_ago = (timezone.now() - timedelta(days=14)).strftime('%Y-%m-%d')
        response = self.client.get(
            f'/api/notifications/?created_after={two_weeks_ago}&created_before={last_week_str}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Last Week Notification')
