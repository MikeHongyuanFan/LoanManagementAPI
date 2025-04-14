from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from borrowers.models import Borrower
from datetime import date

User = get_user_model()

class BorrowerValidationTestCase(TestCase):
    """Test case for borrower API input validation."""
    
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
        
    def test_create_borrower_missing_required_fields(self):
        """Test that creating a borrower with missing required fields returns 400."""
        # Missing first_name, last_name, email, phone_number, state, and dob
        data = {
            'repayment_account': '0987654321'
        }
        response = self.client.post('/api/borrowers/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('first_name', response.data)
        self.assertIn('last_name', response.data)
        self.assertIn('email', response.data)
        self.assertIn('phone_number', response.data)
        self.assertIn('state', response.data)
        self.assertIn('dob', response.data)
        
    def test_create_borrower_invalid_email(self):
        """Test that creating a borrower with invalid email returns 400."""
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'not-an-email',  # Invalid email
            'phone_number': '0987654321',
            'state': 'NY',
            'dob': '1985-05-15',
            'repayment_account': '0987654321'
        }
        response = self.client.post('/api/borrowers/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        
    def test_create_borrower_duplicate_email(self):
        """Test that creating a borrower with duplicate email returns 400."""
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'john.doe@example.com',  # Duplicate email
            'phone_number': '0987654321',
            'state': 'NY',
            'dob': '1985-05-15',
            'repayment_account': '0987654321'
        }
        response = self.client.post('/api/borrowers/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        
    def test_create_borrower_invalid_date_format(self):
        """Test that creating a borrower with invalid date format returns 400."""
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com',
            'phone_number': '0987654321',
            'state': 'NY',
            'dob': '15-05-1985',  # Invalid date format (should be YYYY-MM-DD)
            'repayment_account': '0987654321'
        }
        response = self.client.post('/api/borrowers/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('dob', response.data)
        
    def test_create_borrower_future_date(self):
        """Test that creating a borrower with future date returns 400."""
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com',
            'phone_number': '0987654321',
            'state': 'NY',
            'dob': '2030-05-15',  # Future date
            'repayment_account': '0987654321'
        }
        response = self.client.post('/api/borrowers/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('dob', response.data)
        
    def test_update_borrower_invalid_data(self):
        """Test that updating a borrower with invalid data returns 400."""
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'not-an-email',  # Invalid email
            'phone_number': '1234567890',
            'state': 'CA',
            'dob': '1980-01-01',
            'repayment_account': '1234567890'
        }
        response = self.client.put(f'/api/borrowers/{self.borrower.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        
    def test_partial_update_borrower_invalid_data(self):
        """Test that partially updating a borrower with invalid data returns 400."""
        data = {
            'email': 'not-an-email'  # Invalid email
        }
        response = self.client.patch(f'/api/borrowers/{self.borrower.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        
    def test_retrieve_nonexistent_borrower(self):
        """Test that retrieving a non-existent borrower returns 404."""
        response = self.client.get('/api/borrowers/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_update_nonexistent_borrower(self):
        """Test that updating a non-existent borrower returns 404."""
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone_number': '1234567890',
            'state': 'CA',
            'dob': '1980-01-01',
            'repayment_account': '1234567890'
        }
        response = self.client.put('/api/borrowers/999/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_delete_nonexistent_borrower(self):
        """Test that deleting a non-existent borrower returns 404."""
        response = self.client.delete('/api/borrowers/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_filter_borrowers_invalid_state(self):
        """Test that filtering borrowers with invalid state returns empty results, not an error."""
        response = self.client.get('/api/borrowers/?state=INVALID')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
