import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User
from calculator.models import LoanCalculation, Fee, ApplicationFee
from applications.models import Application
from products.models import Product


class LoanCalculationValidationTests(APITestCase):
    """Test validation for loan calculation endpoints"""
    
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
        
        # Create a test application with required fields
        self.application = Application.objects.create(
            status='pending',
            stage='application',
            gross_loan_amount=300000.00,
            net_loan_amount=300000.00,
            borrower_id=1,  # This might need adjustment
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
        
        # URLs
        self.calculate_url = reverse('loancalculation-calculate')
        self.monthly_payment_url = reverse('monthly-payment')
        self.amortization_schedule_url = reverse('amortization-schedule')
        self.loan_summary_url = reverse('loan-summary')
        self.affordability_url = reverse('affordability')
    
    def test_calculate_missing_required_fields(self):
        """Test that calculate endpoint requires all required fields"""
        # Missing loan_amount
        data = {
            'interest_rate': 5.5,
            'loan_term_years': 30
        }
        response = self.client.post(self.calculate_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('loan_amount', response.data)
        
        # Missing interest_rate
        data = {
            'loan_amount': 300000,
            'loan_term_years': 30
        }
        response = self.client.post(self.calculate_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('interest_rate', response.data)
        
        # Missing loan_term_years
        data = {
            'loan_amount': 300000,
            'interest_rate': 5.5
        }
        response = self.client.post(self.calculate_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('loan_term_years', response.data)
    
    def test_calculate_invalid_loan_amount(self):
        """Test validation for loan_amount field"""
        # Negative loan amount
        data = {
            'loan_amount': -300000,
            'interest_rate': 5.5,
            'loan_term_years': 30
        }
        response = self.client.post(self.calculate_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Non-numeric loan amount
        data = {
            'loan_amount': 'not-a-number',
            'interest_rate': 5.5,
            'loan_term_years': 30
        }
        response = self.client.post(self.calculate_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_calculate_invalid_interest_rate(self):
        """Test validation for interest_rate field"""
        # Negative interest rate
        data = {
            'loan_amount': 300000,
            'interest_rate': -5.5,
            'loan_term_years': 30
        }
        response = self.client.post(self.calculate_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Non-numeric interest rate
        data = {
            'loan_amount': 300000,
            'interest_rate': 'not-a-number',
            'loan_term_years': 30
        }
        response = self.client.post(self.calculate_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_calculate_invalid_loan_term(self):
        """Test validation for loan_term_years field"""
        # Negative loan term
        data = {
            'loan_amount': 300000,
            'interest_rate': 5.5,
            'loan_term_years': -30
        }
        response = self.client.post(self.calculate_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Zero loan term
        data = {
            'loan_amount': 300000,
            'interest_rate': 5.5,
            'loan_term_years': 0
        }
        response = self.client.post(self.calculate_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Loan term too large
        data = {
            'loan_amount': 300000,
            'interest_rate': 5.5,
            'loan_term_years': 100
        }
        response = self.client.post(self.calculate_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Non-numeric loan term
        data = {
            'loan_amount': 300000,
            'interest_rate': 5.5,
            'loan_term_years': 'not-a-number'
        }
        response = self.client.post(self.calculate_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_calculate_invalid_interest_type(self):
        """Test validation for interest_type field"""
        # Invalid interest type
        data = {
            'loan_amount': 300000,
            'interest_rate': 5.5,
            'loan_term_years': 30,
            'interest_type': 'invalid-type'
        }
        response = self.client.post(self.calculate_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_calculate_invalid_compounding_period(self):
        """Test validation for compounding_period field"""
        # Invalid compounding period
        data = {
            'loan_amount': 300000,
            'interest_rate': 5.5,
            'loan_term_years': 30,
            'compounding_period': 'invalid-period'
        }
        response = self.client.post(self.calculate_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_calculate_invalid_application_id(self):
        """Test validation for application_id field"""
        # Non-existent application ID
        data = {
            'loan_amount': 300000,
            'interest_rate': 5.5,
            'loan_term_years': 30,
            'application_id': 9999
        }
        response = self.client.post(self.calculate_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_calculate_valid_data(self):
        """Test that valid data returns a successful response"""
        data = {
            'loan_amount': 300000,
            'interest_rate': 5.5,
            'loan_term_years': 30,
            'interest_type': 'fixed',
            'compounding_period': 'monthly',
            'application_id': self.application.id
        }
        response = self.client.post(self.calculate_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('monthly_payment', response.data)
        self.assertIn('total_payments', response.data)
        self.assertIn('total_interest', response.data)
        self.assertIn('repayment_schedule', response.data)
    
    def test_monthly_payment_invalid_data(self):
        """Test validation for monthly payment endpoint"""
        # Missing loan_amount
        data = {
            'interest_rate': 5.5,
            'term_months': 360
        }
        response = self.client.post(self.monthly_payment_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Non-numeric loan_amount
        data = {
            'loan_amount': 'not-a-number',
            'interest_rate': 5.5,
            'term_months': 360
        }
        response = self.client.post(self.monthly_payment_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_amortization_schedule_invalid_data(self):
        """Test validation for amortization schedule endpoint"""
        # Missing loan_amount
        data = {
            'interest_rate': 5.5,
            'term_months': 360
        }
        response = self.client.post(self.amortization_schedule_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Invalid start_date format
        data = {
            'loan_amount': 300000,
            'interest_rate': 5.5,
            'term_months': 360,
            'start_date': 'not-a-date'
        }
        response = self.client.post(self.amortization_schedule_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_loan_summary_invalid_data(self):
        """Test validation for loan summary endpoint"""
        # Missing loan_amount
        data = {
            'interest_rate': 5.5,
            'term_months': 360
        }
        response = self.client.post(self.loan_summary_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Negative interest_rate
        data = {
            'loan_amount': 300000,
            'interest_rate': -5.5,
            'term_months': 360
        }
        response = self.client.post(self.loan_summary_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_affordability_invalid_data(self):
        """Test validation for affordability endpoint"""
        # Missing monthly_income
        data = {
            'monthly_debts': 1000,
            'interest_rate': 5.5,
            'term_months': 360
        }
        response = self.client.post(self.affordability_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Negative monthly_income
        data = {
            'monthly_income': -5000,
            'monthly_debts': 1000,
            'interest_rate': 5.5,
            'term_months': 360
        }
        response = self.client.post(self.affordability_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Invalid debt_to_income_ratio
        data = {
            'monthly_income': 5000,
            'monthly_debts': 1000,
            'interest_rate': 5.5,
            'term_months': 360,
            'debt_to_income_ratio': 2.0  # Should be between 0 and 1
        }
        response = self.client.post(self.affordability_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
