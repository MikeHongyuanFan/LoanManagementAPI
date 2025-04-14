from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from applications.models import Application
from borrowers.models import Borrower
from products.models import Product

User = get_user_model()

class ApplicationAPITestCase(TestCase):
    """Test case for the application API endpoints."""
    
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
            email='john@example.com'
        )
        self.product = Product.objects.create(
            name='Standard Loan',
            interest_rate=5.5,
            term_months=360
        )
        self.application = Application.objects.create(
            borrower=self.borrower,
            product=self.product,
            loan_amount=250000,
            status='pending',
            created_by=self.user
        )
        self.client.force_authenticate(user=self.user)
        
    def test_list_applications(self):
        """Test that the applications list endpoint returns 200 and correct data structure."""
        response = self.client.get('/api/applications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)
        
    def test_retrieve_application(self):
        """Test that the application detail endpoint returns 200 and correct data."""
        response = self.client.get(f'/api/applications/{self.application.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['loan_amount'], 250000)
        self.assertEqual(response.data['status'], 'pending')
        
    def test_create_application(self):
        """Test that creating an application works correctly."""
        data = {
            'borrower': self.borrower.id,
            'product': self.product.id,
            'loan_amount': 300000,
            'status': 'pending'
        }
        response = self.client.post('/api/applications/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['loan_amount'], 300000)
        self.assertEqual(Application.objects.count(), 2)
        
    def test_update_application(self):
        """Test that updating an application works correctly."""
        data = {
            'borrower': self.borrower.id,
            'product': self.product.id,
            'loan_amount': 275000,
            'status': 'approved'
        }
        response = self.client.put(f'/api/applications/{self.application.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['loan_amount'], 275000)
        self.assertEqual(response.data['status'], 'approved')
        self.application.refresh_from_db()
        self.assertEqual(self.application.loan_amount, 275000)
        
    def test_delete_application(self):
        """Test that deleting an application works correctly."""
        response = self.client.delete(f'/api/applications/{self.application.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Application.objects.count(), 0)
