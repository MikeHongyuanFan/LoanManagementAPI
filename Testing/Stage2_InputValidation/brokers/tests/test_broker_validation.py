from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from brokers.models import Broker

User = get_user_model()

class BrokerValidationTestCase(TestCase):
    """Test case for broker API input validation."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.broker = Broker.objects.create(
            first_name='Michael',
            last_name='Johnson',
            email='michael.johnson@example.com',
            phone_number='1234567890',
            company_name='ABC Mortgage',
            license_number='BRK12345',
            years_of_experience=5
        )
        self.client.force_authenticate(user=self.user)
        
    def test_create_broker_missing_required_fields(self):
        """Test that creating a broker with missing required fields returns 400."""
        # Missing first_name, last_name, email, and phone_number
        data = {
            'company_name': 'XYZ Loans',
            'license_number': 'BRK67890',
            'years_of_experience': 8
        }
        response = self.client.post('/api/brokers/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('first_name', response.data)
        self.assertIn('last_name', response.data)
        self.assertIn('email', response.data)
        self.assertIn('phone_number', response.data)
        
    def test_create_broker_invalid_email(self):
        """Test that creating a broker with invalid email returns 400."""
        data = {
            'first_name': 'Sarah',
            'last_name': 'Williams',
            'email': 'not-an-email',  # Invalid email
            'phone_number': '0987654321',
            'company_name': 'XYZ Loans',
            'license_number': 'BRK67890',
            'years_of_experience': 8
        }
        response = self.client.post('/api/brokers/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        
    def test_create_broker_duplicate_email(self):
        """Test that creating a broker with duplicate email returns 400."""
        data = {
            'first_name': 'Sarah',
            'last_name': 'Williams',
            'email': 'michael.johnson@example.com',  # Duplicate email
            'phone_number': '0987654321',
            'company_name': 'XYZ Loans',
            'license_number': 'BRK67890',
            'years_of_experience': 8
        }
        response = self.client.post('/api/brokers/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        
    def test_create_broker_negative_experience(self):
        """Test that creating a broker with negative years of experience returns 400."""
        data = {
            'first_name': 'Sarah',
            'last_name': 'Williams',
            'email': 'sarah.williams@example.com',
            'phone_number': '0987654321',
            'company_name': 'XYZ Loans',
            'license_number': 'BRK67890',
            'years_of_experience': -2  # Negative years
        }
        response = self.client.post('/api/brokers/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('years_of_experience', response.data)
        
    def test_update_broker_invalid_data(self):
        """Test that updating a broker with invalid data returns 400."""
        data = {
            'first_name': 'Michael',
            'last_name': 'Johnson',
            'email': 'not-an-email',  # Invalid email
            'phone_number': '1234567890',
            'company_name': 'Premium Mortgage',
            'license_number': 'BRK12345',
            'years_of_experience': 7
        }
        response = self.client.put(f'/api/brokers/{self.broker.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        
    def test_partial_update_broker_invalid_data(self):
        """Test that partially updating a broker with invalid data returns 400."""
        data = {
            'email': 'not-an-email'  # Invalid email
        }
        response = self.client.patch(f'/api/brokers/{self.broker.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        
    def test_retrieve_nonexistent_broker(self):
        """Test that retrieving a non-existent broker returns 404."""
        response = self.client.get('/api/brokers/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_update_nonexistent_broker(self):
        """Test that updating a non-existent broker returns 404."""
        data = {
            'first_name': 'Michael',
            'last_name': 'Johnson',
            'email': 'michael.johnson@example.com',
            'phone_number': '1234567890',
            'company_name': 'Premium Mortgage',
            'license_number': 'BRK12345',
            'years_of_experience': 7
        }
        response = self.client.put('/api/brokers/999/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_delete_nonexistent_broker(self):
        """Test that deleting a non-existent broker returns 404."""
        response = self.client.delete('/api/brokers/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_filter_brokers_invalid_experience(self):
        """Test that filtering brokers with invalid experience values returns 400."""
        response = self.client.get('/api/brokers/?min_experience=abc')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response = self.client.get('/api/brokers/?max_experience=xyz')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
