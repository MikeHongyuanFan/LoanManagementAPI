from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from brokers.models import Broker

User = get_user_model()

class BrokerAPITestCase(TestCase):
    """Test case for the broker API endpoints."""
    
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
        
    def test_list_brokers(self):
        """Test that the brokers list endpoint returns 200 and correct data structure."""
        response = self.client.get('/api/brokers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)
        
    def test_retrieve_broker(self):
        """Test that the broker detail endpoint returns 200 and correct data."""
        response = self.client.get(f'/api/brokers/{self.broker.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Michael')
        self.assertEqual(response.data['last_name'], 'Johnson')
        self.assertEqual(response.data['company_name'], 'ABC Mortgage')
        self.assertEqual(response.data['license_number'], 'BRK12345')
        
    def test_create_broker(self):
        """Test that creating a broker works correctly."""
        data = {
            'first_name': 'Sarah',
            'last_name': 'Williams',
            'email': 'sarah.williams@example.com',
            'phone_number': '0987654321',
            'company_name': 'XYZ Loans',
            'license_number': 'BRK67890',
            'years_of_experience': 8
        }
        response = self.client.post('/api/brokers/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['first_name'], 'Sarah')
        self.assertEqual(response.data['company_name'], 'XYZ Loans')
        self.assertEqual(Broker.objects.count(), 2)
        
    def test_update_broker(self):
        """Test that updating a broker works correctly."""
        data = {
            'first_name': 'Michael',
            'last_name': 'Johnson',
            'email': 'michael.johnson@example.com',
            'phone_number': '1234567890',
            'company_name': 'Premium Mortgage',  # Updated company name
            'license_number': 'BRK12345',
            'years_of_experience': 7  # Updated years of experience
        }
        response = self.client.put(f'/api/brokers/{self.broker.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company_name'], 'Premium Mortgage')
        self.assertEqual(response.data['years_of_experience'], 7)
        self.broker.refresh_from_db()
        self.assertEqual(self.broker.company_name, 'Premium Mortgage')
        self.assertEqual(self.broker.years_of_experience, 7)
        
    def test_partial_update_broker(self):
        """Test that partially updating a broker works correctly."""
        data = {
            'license_number': 'BRK99999'  # Only update license number
        }
        response = self.client.patch(f'/api/brokers/{self.broker.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['license_number'], 'BRK99999')
        self.broker.refresh_from_db()
        self.assertEqual(self.broker.license_number, 'BRK99999')
        
    def test_delete_broker(self):
        """Test that deleting a broker works correctly."""
        response = self.client.delete(f'/api/brokers/{self.broker.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Broker.objects.count(), 0)
        
    def test_search_brokers(self):
        """Test that searching brokers works correctly."""
        # Create additional brokers for search testing
        Broker.objects.create(
            first_name='David',
            last_name='Johnson',
            email='david.johnson@example.com',
            phone_number='5551234567',
            company_name='Johnson Mortgage',
            license_number='BRK54321',
            years_of_experience=10
        )
        Broker.objects.create(
            first_name='Emily',
            last_name='Brown',
            email='emily.brown@example.com',
            phone_number='5559876543',
            company_name='ABC Mortgage',  # Same company as first broker
            license_number='BRK13579',
            years_of_experience=3
        )
        
        # Search by last name
        response = self.client.get('/api/brokers/?search=Johnson')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        
        # Search by company name
        response = self.client.get('/api/brokers/?search=ABC Mortgage')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        
    def test_filter_brokers_by_experience(self):
        """Test that filtering brokers by years of experience works correctly."""
        # Create additional brokers for filter testing
        Broker.objects.create(
            first_name='David',
            last_name='Johnson',
            email='david.johnson@example.com',
            phone_number='5551234567',
            company_name='Johnson Mortgage',
            license_number='BRK54321',
            years_of_experience=10
        )
        Broker.objects.create(
            first_name='Emily',
            last_name='Brown',
            email='emily.brown@example.com',
            phone_number='5559876543',
            company_name='ABC Mortgage',
            license_number='BRK13579',
            years_of_experience=3
        )
        
        # Filter by minimum experience
        response = self.client.get('/api/brokers/?min_experience=5')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        
        # Filter by maximum experience
        response = self.client.get('/api/brokers/?max_experience=5')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        
        # Filter by experience range
        response = self.client.get('/api/brokers/?min_experience=6&max_experience=12')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['first_name'], 'David')
