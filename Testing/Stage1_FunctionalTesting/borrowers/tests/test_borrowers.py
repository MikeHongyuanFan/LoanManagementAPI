from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from borrowers.models import Borrower
from datetime import date

User = get_user_model()

class BorrowerAPITestCase(TestCase):
    """Test case for the borrower API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.borrower = Borrower.objects.create(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone_number='1234567890',
            state='CA',
            dob=date(1980, 1, 1),
            repayment_account='1234567890'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_list_borrowers(self):
        """Test that the borrowers list endpoint returns 200 and correct data structure."""
        response = self.client.get('/api/borrowers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)
        
    def test_retrieve_borrower(self):
        """Test that the borrower detail endpoint returns 200 and correct data."""
        response = self.client.get(f'/api/borrowers/{self.borrower.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'John')
        self.assertEqual(response.data['last_name'], 'Doe')
        self.assertEqual(response.data['email'], 'john.doe@example.com')
        
    def test_create_borrower(self):
        """Test that creating a borrower works correctly."""
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com',
            'phone_number': '0987654321',
            'state': 'NY',
            'dob': '1985-05-15',
            'repayment_account': '0987654321'
        }
        response = self.client.post('/api/borrowers/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['first_name'], 'Jane')
        self.assertEqual(response.data['last_name'], 'Smith')
        self.assertEqual(Borrower.objects.count(), 2)
        
    def test_update_borrower(self):
        """Test that updating a borrower works correctly."""
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone_number': '1234567890',
            'state': 'NY',  # Updated state
            'dob': '1980-01-01',
            'repayment_account': '9876543210'  # Updated account
        }
        response = self.client.put(f'/api/borrowers/{self.borrower.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['state'], 'NY')
        self.assertEqual(response.data['repayment_account'], '9876543210')
        self.borrower.refresh_from_db()
        self.assertEqual(self.borrower.state, 'NY')
        self.assertEqual(self.borrower.repayment_account, '9876543210')
        
    def test_partial_update_borrower(self):
        """Test that partially updating a borrower works correctly."""
        data = {
            'phone_number': '5555555555'  # Only update phone number
        }
        response = self.client.patch(f'/api/borrowers/{self.borrower.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone_number'], '5555555555')
        self.borrower.refresh_from_db()
        self.assertEqual(self.borrower.phone_number, '5555555555')
        
    def test_delete_borrower(self):
        """Test that deleting a borrower works correctly."""
        response = self.client.delete(f'/api/borrowers/{self.borrower.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Borrower.objects.count(), 0)
        
    def test_search_borrowers(self):
        """Test that searching borrowers works correctly."""
        # Create additional borrowers for search testing
        Borrower.objects.create(
            first_name='Jane',
            last_name='Doe',
            email='jane.doe@example.com',
            phone_number='0987654321',
            state='CA',
            dob=date(1982, 3, 15),
            repayment_account='2345678901'
        )
        Borrower.objects.create(
            first_name='Bob',
            last_name='Smith',
            email='bob.smith@example.com',
            phone_number='1122334455',
            state='NY',
            dob=date(1975, 8, 22),
            repayment_account='3456789012'
        )
        
        # Search by last name
        response = self.client.get('/api/borrowers/?search=Doe')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        
        # Search by email
        response = self.client.get('/api/borrowers/?search=bob.smith')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['first_name'], 'Bob')
        
    def test_filter_borrowers_by_state(self):
        """Test that filtering borrowers by state works correctly."""
        # Create additional borrowers for filter testing
        Borrower.objects.create(
            first_name='Jane',
            last_name='Doe',
            email='jane.doe@example.com',
            phone_number='0987654321',
            state='CA',
            dob=date(1982, 3, 15),
            repayment_account='2345678901'
        )
        Borrower.objects.create(
            first_name='Bob',
            last_name='Smith',
            email='bob.smith@example.com',
            phone_number='1122334455',
            state='NY',
            dob=date(1975, 8, 22),
            repayment_account='3456789012'
        )
        
        # Filter by CA state
        response = self.client.get('/api/borrowers/?state=CA')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        
        # Filter by NY state
        response = self.client.get('/api/borrowers/?state=NY')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['first_name'], 'Bob')
