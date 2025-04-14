from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from products.models import Product, Fee
from decimal import Decimal

User = get_user_model()

class ProductValidationTestCase(TestCase):
    """Test case for product input validation."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.product = Product.objects.create(
            name='Standard Loan',
            description='Standard fixed-rate mortgage loan',
            interest_rate=5.5,
            term_months=360,
            min_loan_amount=50000,
            max_loan_amount=1000000,
            min_credit_score=650,
            is_active=True
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_product_missing_required_fields(self):
        """Test that creating a product without required fields returns 400."""
        data = {
            # Missing required 'name' field
            'description': 'Premium mortgage with lower interest rate',
            'interest_rate': 4.5,
            'term_months': 360
        }
        response = self.client.post('/api/products/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
    
    def test_create_product_invalid_interest_rate(self):
        """Test that creating a product with invalid interest rate returns 400."""
        data = {
            'name': 'Premium Loan',
            'description': 'Premium mortgage with lower interest rate',
            'interest_rate': -1.5,  # Negative interest rate
            'term_months': 360,
            'min_loan_amount': 100000,
            'max_loan_amount': 2000000,
            'min_credit_score': 700,
            'is_active': True
        }
        response = self.client.post('/api/products/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('interest_rate', response.data)
    
    def test_create_product_invalid_term_months(self):
        """Test that creating a product with invalid term months returns 400."""
        data = {
            'name': 'Premium Loan',
            'description': 'Premium mortgage with lower interest rate',
            'interest_rate': 4.5,
            'term_months': -12,  # Negative term months
            'min_loan_amount': 100000,
            'max_loan_amount': 2000000,
            'min_credit_score': 700,
            'is_active': True
        }
        response = self.client.post('/api/products/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('term_months', response.data)
    
    def test_create_product_invalid_loan_amount_range(self):
        """Test that creating a product with invalid loan amount range returns 400."""
        data = {
            'name': 'Premium Loan',
            'description': 'Premium mortgage with lower interest rate',
            'interest_rate': 4.5,
            'term_months': 360,
            'min_loan_amount': 200000,
            'max_loan_amount': 100000,  # Max less than min
            'min_credit_score': 700,
            'is_active': True
        }
        response = self.client.post('/api/products/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
    
    def test_create_product_invalid_credit_score(self):
        """Test that creating a product with invalid credit score returns 400."""
        data = {
            'name': 'Premium Loan',
            'description': 'Premium mortgage with lower interest rate',
            'interest_rate': 4.5,
            'term_months': 360,
            'min_loan_amount': 100000,
            'max_loan_amount': 2000000,
            'min_credit_score': 900,  # Credit score too high
            'is_active': True
        }
        response = self.client.post('/api/products/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('min_credit_score', response.data)
    
    def test_create_product_name_too_long(self):
        """Test that creating a product with a name that's too long returns 400."""
        data = {
            'name': 'P' * 101,  # 101 characters, but max is 100
            'description': 'Premium mortgage with lower interest rate',
            'interest_rate': 4.5,
            'term_months': 360,
            'min_loan_amount': 100000,
            'max_loan_amount': 2000000,
            'min_credit_score': 700,
            'is_active': True
        }
        response = self.client.post('/api/products/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
    
    def test_update_product_invalid_data(self):
        """Test that updating a product with invalid data returns 400."""
        data = {
            'interest_rate': 30.5,  # Interest rate too high
        }
        response = self.client.patch(f'/api/products/{self.product.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('interest_rate', response.data)
    
    def test_filter_products_invalid_parameters(self):
        """Test that filtering products with invalid parameters returns appropriate response."""
        response = self.client.get('/api/products/?min_interest_rate=abc')  # Non-numeric value
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response = self.client.get('/api/products/?loan_amount=invalid')  # Non-numeric value
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response = self.client.get('/api/products/?credit_score=-100')  # Negative credit score
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class FeeValidationTestCase(TestCase):
    """Test case for fee input validation."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.product = Product.objects.create(
            name='Standard Loan',
            description='Standard fixed-rate mortgage loan',
            interest_rate=5.5,
            term_months=360,
            min_loan_amount=50000,
            max_loan_amount=1000000,
            min_credit_score=650,
            is_active=True
        )
        self.fee = Fee.objects.create(
            product=self.product,
            name='Application Fee',
            amount=500,
            is_percentage=False
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_fee_missing_required_fields(self):
        """Test that creating a fee without required fields returns 400."""
        data = {
            # Missing required 'name' field
            'amount': 250,
            'is_percentage': False
        }
        response = self.client.post(f'/api/products/{self.product.id}/fees/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
    
    def test_create_fee_invalid_amount(self):
        """Test that creating a fee with invalid amount returns 400."""
        data = {
            'name': 'Processing Fee',
            'amount': -100,  # Negative amount
            'is_percentage': False
        }
        response = self.client.post(f'/api/products/{self.product.id}/fees/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('amount', response.data)
    
    def test_create_fee_invalid_percentage(self):
        """Test that creating a fee with invalid percentage returns 400."""
        data = {
            'name': 'Processing Fee',
            'amount': 101,  # Percentage over 100%
            'is_percentage': True
        }
        response = self.client.post(f'/api/products/{self.product.id}/fees/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('amount', response.data)
    
    def test_create_fee_name_too_long(self):
        """Test that creating a fee with a name that's too long returns 400."""
        data = {
            'name': 'F' * 101,  # 101 characters, but max is 100
            'amount': 250,
            'is_percentage': False
        }
        response = self.client.post(f'/api/products/{self.product.id}/fees/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
    
    def test_update_fee_invalid_data(self):
        """Test that updating a fee with invalid data returns 400."""
        data = {
            'amount': -50,  # Negative amount
        }
        response = self.client.patch(f'/api/products/{self.product.id}/fees/{self.fee.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('amount', response.data)
    
    def test_create_fee_for_nonexistent_product(self):
        """Test that creating a fee for a nonexistent product returns 404."""
        data = {
            'name': 'Processing Fee',
            'amount': 250,
            'is_percentage': False
        }
        response = self.client.post('/api/products/9999/fees/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
