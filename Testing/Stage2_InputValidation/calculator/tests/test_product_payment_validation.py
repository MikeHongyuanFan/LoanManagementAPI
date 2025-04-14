import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User
from products.models import Product, Fee


class ProductPaymentValidationTests(APITestCase):
    """Test validation for product payment endpoints"""
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='testpassword'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test products
        self.product1 = Product.objects.create(
            name='Standard Loan',
            interest_rate=5.5,
            term_months=360
        )
        
        self.product2 = Product.objects.create(
            name='Premium Loan',
            interest_rate=4.5,
            term_months=360
        )
        
        # Create test fees
        self.fee1 = Fee.objects.create(
            name='Application Fee',
            amount=500,
            is_percentage=False
        )
        
        self.fee2 = Fee.objects.create(
            name='Origination Fee',
            amount=1.0,  # 1% of loan amount
            is_percentage=True
        )
        
        # Add fees to products
        self.product1.fees.add(self.fee1, self.fee2)
        self.product2.fees.add(self.fee1, self.fee2)
        
        # URLs
        self.product_payment_url = reverse('product-payment')
        self.compare_products_url = reverse('compare-products')
    
    def test_product_payment_missing_required_fields(self):
        """Test that product payment endpoint requires all required fields"""
        # Missing product_id
        data = {
            'loan_amount': 300000
        }
        response = self.client.post(self.product_payment_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Missing loan_amount
        data = {
            'product_id': self.product1.id
        }
        response = self.client.post(self.product_payment_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_product_payment_invalid_product_id(self):
        """Test validation for product_id field"""
        # Non-existent product ID
        data = {
            'product_id': 9999,
            'loan_amount': 300000
        }
        response = self.client.post(self.product_payment_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Non-numeric product ID
        data = {
            'product_id': 'not-a-number',
            'loan_amount': 300000
        }
        response = self.client.post(self.product_payment_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_product_payment_invalid_loan_amount(self):
        """Test validation for loan_amount field"""
        # Negative loan amount
        data = {
            'product_id': self.product1.id,
            'loan_amount': -300000
        }
        response = self.client.post(self.product_payment_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Zero loan amount
        data = {
            'product_id': self.product1.id,
            'loan_amount': 0
        }
        response = self.client.post(self.product_payment_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Non-numeric loan amount
        data = {
            'product_id': self.product1.id,
            'loan_amount': 'not-a-number'
        }
        response = self.client.post(self.product_payment_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_product_payment_valid_data(self):
        """Test that valid data returns a successful response"""
        data = {
            'product_id': self.product1.id,
            'loan_amount': 300000
        }
        response = self.client.post(self.product_payment_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('monthly_payment', response.data)
        self.assertIn('fees', response.data)
        self.assertIn('total_fees', response.data)
    
    def test_compare_products_missing_required_fields(self):
        """Test that compare products endpoint requires all required fields"""
        # Missing product_ids
        data = {
            'loan_amount': 300000
        }
        response = self.client.post(self.compare_products_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Missing loan_amount
        data = {
            'product_ids': [self.product1.id, self.product2.id]
        }
        response = self.client.post(self.compare_products_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_compare_products_invalid_product_ids(self):
        """Test validation for product_ids field"""
        # Empty product_ids list
        data = {
            'product_ids': [],
            'loan_amount': 300000
        }
        response = self.client.post(self.compare_products_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Non-existent product ID
        data = {
            'product_ids': [self.product1.id, 9999],
            'loan_amount': 300000
        }
        response = self.client.post(self.compare_products_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Non-numeric product ID
        data = {
            'product_ids': [self.product1.id, 'not-a-number'],
            'loan_amount': 300000
        }
        response = self.client.post(self.compare_products_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_compare_products_invalid_loan_amount(self):
        """Test validation for loan_amount field"""
        # Negative loan amount
        data = {
            'product_ids': [self.product1.id, self.product2.id],
            'loan_amount': -300000
        }
        response = self.client.post(self.compare_products_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Zero loan amount
        data = {
            'product_ids': [self.product1.id, self.product2.id],
            'loan_amount': 0
        }
        response = self.client.post(self.compare_products_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Non-numeric loan amount
        data = {
            'product_ids': [self.product1.id, self.product2.id],
            'loan_amount': 'not-a-number'
        }
        response = self.client.post(self.compare_products_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_compare_products_valid_data(self):
        """Test that valid data returns a successful response"""
        data = {
            'product_ids': [self.product1.id, self.product2.id],
            'loan_amount': 300000
        }
        response = self.client.post(self.compare_products_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should return data for both products
        
        for product_data in response.data:
            self.assertIn('product_id', product_data)
            self.assertIn('product_name', product_data)
            self.assertIn('interest_rate', product_data)
            self.assertIn('monthly_payment', product_data)
            self.assertIn('total_payments', product_data)
            self.assertIn('total_interest', product_data)
            self.assertIn('fees', product_data)
            self.assertIn('total_fees', product_data)
            self.assertIn('total_cost', product_data)
