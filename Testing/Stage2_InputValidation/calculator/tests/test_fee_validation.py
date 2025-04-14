import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User
from calculator.models import Fee, ApplicationFee
from applications.models import Application
from products.models import Product


class FeeValidationTests(APITestCase):
    """Test validation for fee endpoints"""
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='testpassword'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create a test product
        self.product = Product.objects.create(
            name='Test Product',
            interest_rate=5.5,
            term_months=360
        )
        
        # Create a test application
        self.application = Application.objects.create(
            title='Test Application',
            product=self.product
        )
        
        # Create a test fee
        self.fee = Fee.objects.create(
            name='Test Fee',
            fee_type='application',
            calculation_method='fixed',
            amount=500.00,
            is_active=True
        )
        self.fee.products.add(self.product)
        
        # Create a test application fee
        self.application_fee = ApplicationFee.objects.create(
            application=self.application,
            fee=self.fee,
            calculated_amount=500.00
        )
        
        # URLs
        self.fee_list_url = reverse('fee-list')
        self.fee_detail_url = reverse('fee-detail', args=[self.fee.id])
        self.application_fee_list_url = reverse('applicationfee-list')
        self.application_fee_detail_url = reverse('applicationfee-detail', args=[self.application_fee.id])
        self.application_fee_waive_url = reverse('applicationfee-waive', args=[self.application_fee.id])
    
    def test_create_fee_missing_required_fields(self):
        """Test that fee creation requires all required fields"""
        # Missing name
        data = {
            'fee_type': 'application',
            'calculation_method': 'fixed',
            'amount': 500.00
        }
        response = self.client.post(self.fee_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        
        # Missing fee_type
        data = {
            'name': 'New Fee',
            'calculation_method': 'fixed',
            'amount': 500.00
        }
        response = self.client.post(self.fee_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('fee_type', response.data)
        
        # Missing calculation_method
        data = {
            'name': 'New Fee',
            'fee_type': 'application',
            'amount': 500.00
        }
        response = self.client.post(self.fee_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('calculation_method', response.data)
        
        # Missing amount
        data = {
            'name': 'New Fee',
            'fee_type': 'application',
            'calculation_method': 'fixed'
        }
        response = self.client.post(self.fee_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('amount', response.data)
    
    def test_create_fee_invalid_fee_type(self):
        """Test validation for fee_type field"""
        data = {
            'name': 'New Fee',
            'fee_type': 'invalid-type',
            'calculation_method': 'fixed',
            'amount': 500.00
        }
        response = self.client.post(self.fee_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('fee_type', response.data)
    
    def test_create_fee_invalid_calculation_method(self):
        """Test validation for calculation_method field"""
        data = {
            'name': 'New Fee',
            'fee_type': 'application',
            'calculation_method': 'invalid-method',
            'amount': 500.00
        }
        response = self.client.post(self.fee_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('calculation_method', response.data)
    
    def test_create_fee_invalid_amount(self):
        """Test validation for amount field"""
        # Negative amount
        data = {
            'name': 'New Fee',
            'fee_type': 'application',
            'calculation_method': 'fixed',
            'amount': -500.00
        }
        response = self.client.post(self.fee_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('amount', response.data)
        
        # Non-numeric amount
        data = {
            'name': 'New Fee',
            'fee_type': 'application',
            'calculation_method': 'fixed',
            'amount': 'not-a-number'
        }
        response = self.client.post(self.fee_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('amount', response.data)
    
    def test_create_fee_invalid_products(self):
        """Test validation for products field"""
        # Non-existent product ID
        data = {
            'name': 'New Fee',
            'fee_type': 'application',
            'calculation_method': 'fixed',
            'amount': 500.00,
            'products': [9999]
        }
        response = self.client.post(self.fee_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('products', response.data)
    
    def test_update_fee_invalid_data(self):
        """Test validation for fee update"""
        # Invalid fee_type
        data = {
            'fee_type': 'invalid-type'
        }
        response = self.client.patch(self.fee_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('fee_type', response.data)
        
        # Negative amount
        data = {
            'amount': -500.00
        }
        response = self.client.patch(self.fee_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('amount', response.data)
    
    def test_create_application_fee_missing_required_fields(self):
        """Test that application fee creation requires all required fields"""
        # Missing application
        data = {
            'fee': self.fee.id,
            'calculated_amount': 500.00
        }
        response = self.client.post(self.application_fee_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('application', response.data)
        
        # Missing fee
        data = {
            'application': self.application.id,
            'calculated_amount': 500.00
        }
        response = self.client.post(self.application_fee_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('fee', response.data)
        
        # Missing calculated_amount
        data = {
            'application': self.application.id,
            'fee': self.fee.id
        }
        response = self.client.post(self.application_fee_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('calculated_amount', response.data)
    
    def test_create_application_fee_invalid_application(self):
        """Test validation for application field"""
        data = {
            'application': 9999,
            'fee': self.fee.id,
            'calculated_amount': 500.00
        }
        response = self.client.post(self.application_fee_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('application', response.data)
    
    def test_create_application_fee_invalid_fee(self):
        """Test validation for fee field"""
        data = {
            'application': self.application.id,
            'fee': 9999,
            'calculated_amount': 500.00
        }
        response = self.client.post(self.application_fee_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('fee', response.data)
    
    def test_create_application_fee_invalid_calculated_amount(self):
        """Test validation for calculated_amount field"""
        # Negative amount
        data = {
            'application': self.application.id,
            'fee': self.fee.id,
            'calculated_amount': -500.00
        }
        response = self.client.post(self.application_fee_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('calculated_amount', response.data)
        
        # Non-numeric amount
        data = {
            'application': self.application.id,
            'fee': self.fee.id,
            'calculated_amount': 'not-a-number'
        }
        response = self.client.post(self.application_fee_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('calculated_amount', response.data)
    
    def test_waive_fee_missing_waiver_reason(self):
        """Test validation for fee waiver"""
        data = {}  # Missing waiver_reason
        response = self.client.post(self.application_fee_waive_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('waiver_reason', response.data)
    
    def test_waive_fee_valid_data(self):
        """Test that valid data returns a successful response"""
        data = {
            'waiver_reason': 'Customer loyalty discount'
        }
        response = self.client.post(self.application_fee_waive_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_waived'])
        self.assertEqual(response.data['waiver_reason'], 'Customer loyalty discount')
