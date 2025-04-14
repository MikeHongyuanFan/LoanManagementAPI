from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from applications.models import Application
from borrowers.models import Borrower
from products.models import Product
import datetime

User = get_user_model()

class ApplicationValidationTestCase(TestCase):
    """Test case for application API input validation."""
    
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
            email='john@example.com',
            phone_number='1234567890',
            state='CA',
            dob=datetime.date(1980, 1, 1)
        )
        self.product = Product.objects.create(
            name='Standard Loan',
            description='A standard loan product'
        )
        self.application = Application.objects.create(
            borrower=self.borrower,
            product=self.product,
            gross_loan_amount=250000,
            net_loan_amount=240000,
            status='draft'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_create_application_missing_required_fields(self):
        """Test that creating an application with missing required fields returns 400."""
        # Missing borrower, product, gross_loan_amount, net_loan_amount
        data = {
            'status': 'draft'
        }
        response = self.client.post('/api/applications/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('borrower', response.data)
        self.assertIn('product', response.data)
        self.assertIn('gross_loan_amount', response.data)
        self.assertIn('net_loan_amount', response.data)
        
    def test_create_application_invalid_loan_amounts(self):
        """Test that creating an application with invalid loan amounts returns 400."""
        # Negative loan amounts
        data = {
            'borrower': self.borrower.id,
            'product': self.product.id,
            'gross_loan_amount': -10000,
            'net_loan_amount': -9000,
            'status': 'draft'
        }
        response = self.client.post('/api/applications/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('gross_loan_amount', response.data)
        self.assertIn('net_loan_amount', response.data)
        
    def test_create_application_net_greater_than_gross(self):
        """Test that creating an application with net amount greater than gross amount returns 400."""
        data = {
            'borrower': self.borrower.id,
            'product': self.product.id,
            'gross_loan_amount': 100000,
            'net_loan_amount': 110000,  # Net greater than gross
            'status': 'draft'
        }
        response = self.client.post('/api/applications/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('net_loan_amount', response.data)
        
    def test_create_application_invalid_status(self):
        """Test that creating an application with invalid status returns 400."""
        data = {
            'borrower': self.borrower.id,
            'product': self.product.id,
            'gross_loan_amount': 300000,
            'net_loan_amount': 290000,
            'status': 'invalid_status'  # Invalid status
        }
        response = self.client.post('/api/applications/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('status', response.data)
        
    def test_create_application_invalid_stage(self):
        """Test that creating an application with invalid stage returns 400."""
        data = {
            'borrower': self.borrower.id,
            'product': self.product.id,
            'gross_loan_amount': 300000,
            'net_loan_amount': 290000,
            'status': 'draft',
            'stage': 'invalid_stage'  # Invalid stage
        }
        response = self.client.post('/api/applications/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('stage', response.data)
        
    def test_update_application_invalid_data(self):
        """Test that updating an application with invalid data returns 400."""
        data = {
            'borrower': self.borrower.id,
            'product': self.product.id,
            'gross_loan_amount': -5000,  # Negative amount
            'net_loan_amount': 240000,
            'status': 'draft'
        }
        response = self.client.put(f'/api/applications/{self.application.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('gross_loan_amount', response.data)
        
    def test_transition_application_invalid_status(self):
        """Test that transitioning an application with invalid status returns 400."""
        data = {
            'status': 'invalid_status'
        }
        response = self.client.post(f'/api/applications/{self.application.id}/transition/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('status', response.data)
        
    def test_transition_application_invalid_stage(self):
        """Test that transitioning an application with invalid stage returns 400."""
        data = {
            'stage': 'invalid_stage'
        }
        response = self.client.post(f'/api/applications/{self.application.id}/transition/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('stage', response.data)
        
    def test_retrieve_nonexistent_application(self):
        """Test that retrieving a non-existent application returns 404."""
        response = self.client.get('/api/applications/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_update_nonexistent_application(self):
        """Test that updating a non-existent application returns 404."""
        data = {
            'borrower': self.borrower.id,
            'product': self.product.id,
            'gross_loan_amount': 275000,
            'net_loan_amount': 265000,
            'status': 'approved'
        }
        response = self.client.put('/api/applications/999/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_delete_nonexistent_application(self):
        """Test that deleting a non-existent application returns 404."""
        response = self.client.delete('/api/applications/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_transition_nonexistent_application(self):
        """Test that transitioning a non-existent application returns 404."""
        data = {
            'status': 'approved',
            'stage': 'approval'
        }
        response = self.client.post('/api/applications/999/transition/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_duplicate_nonexistent_application(self):
        """Test that duplicating a non-existent application returns 404."""
        response = self.client.post('/api/applications/999/duplicate/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
