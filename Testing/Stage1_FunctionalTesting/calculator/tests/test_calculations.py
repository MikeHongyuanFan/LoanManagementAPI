from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from products.models import Product, Fee

User = get_user_model()

class LoanCalculatorAPITestCase(TestCase):
    """Test case for the loan calculator API endpoints."""
    
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
        # Add fees to the product
        Fee.objects.create(
            product=self.product,
            name='Application Fee',
            amount=500,
            is_percentage=False
        )
        Fee.objects.create(
            product=self.product,
            name='Origination Fee',
            amount=1.0,
            is_percentage=True
        )
        self.client.force_authenticate(user=self.user)
        
    def test_calculate_monthly_payment(self):
        """Test that calculating monthly payment works correctly."""
        data = {
            'loan_amount': 300000,
            'interest_rate': 5.5,
            'term_months': 360
        }
        response = self.client.post('/api/calculator/monthly-payment/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('monthly_payment', response.data)
        self.assertAlmostEqual(response.data['monthly_payment'], 1703.37, places=2)
        
    def test_calculate_amortization_schedule(self):
        """Test that calculating amortization schedule works correctly."""
        data = {
            'loan_amount': 300000,
            'interest_rate': 5.5,
            'term_months': 360
        }
        response = self.client.post('/api/calculator/amortization-schedule/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('schedule', response.data)
        self.assertEqual(len(response.data['schedule']), 360)  # 30 years * 12 months
        
        # Check first payment
        first_payment = response.data['schedule'][0]
        self.assertIn('payment_number', first_payment)
        self.assertIn('payment_amount', first_payment)
        self.assertIn('principal', first_payment)
        self.assertIn('interest', first_payment)
        self.assertIn('remaining_balance', first_payment)
        
        # Verify that the last payment reduces the balance to zero (or very close)
        last_payment = response.data['schedule'][-1]
        self.assertAlmostEqual(last_payment['remaining_balance'], 0, places=2)
        
    def test_calculate_loan_summary(self):
        """Test that calculating loan summary works correctly."""
        data = {
            'loan_amount': 300000,
            'interest_rate': 5.5,
            'term_months': 360
        }
        response = self.client.post('/api/calculator/loan-summary/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('monthly_payment', response.data)
        self.assertIn('total_payments', response.data)
        self.assertIn('total_interest', response.data)
        self.assertIn('total_cost', response.data)
        
        # Verify calculations
        self.assertAlmostEqual(response.data['monthly_payment'], 1703.37, places=2)
        self.assertAlmostEqual(response.data['total_payments'], 613213.20, places=2)
        self.assertAlmostEqual(response.data['total_interest'], 313213.20, places=2)
        self.assertAlmostEqual(response.data['total_cost'], 613213.20, places=2)
        
    def test_calculate_product_payment(self):
        """Test that calculating payment for a specific product works correctly."""
        data = {
            'product_id': self.product.id,
            'loan_amount': 300000
        }
        response = self.client.post('/api/calculator/product-payment/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('monthly_payment', response.data)
        self.assertIn('fees', response.data)
        self.assertIn('total_fees', response.data)
        
        # Verify calculations
        self.assertAlmostEqual(response.data['monthly_payment'], 1703.37, places=2)
        self.assertEqual(len(response.data['fees']), 2)
        
        # Check fees
        application_fee = next(fee for fee in response.data['fees'] if fee['name'] == 'Application Fee')
        origination_fee = next(fee for fee in response.data['fees'] if fee['name'] == 'Origination Fee')
        
        self.assertEqual(application_fee['amount'], 500)
        self.assertAlmostEqual(origination_fee['amount'], 3000, places=2)  # 1% of 300000
        
        # Total fees should be sum of all fees
        self.assertAlmostEqual(response.data['total_fees'], 3500, places=2)
        
    def test_compare_products(self):
        """Test that comparing multiple products works correctly."""
        # Create a second product for comparison
        premium_product = Product.objects.create(
            name='Premium Loan',
            description='Premium mortgage with lower interest rate',
            interest_rate=4.5,
            term_months=360,
            min_loan_amount=100000,
            max_loan_amount=2000000,
            min_credit_score=700,
            is_active=True
        )
        Fee.objects.create(
            product=premium_product,
            name='Application Fee',
            amount=750,
            is_percentage=False
        )
        Fee.objects.create(
            product=premium_product,
            name='Origination Fee',
            amount=1.5,
            is_percentage=True
        )
        
        data = {
            'loan_amount': 300000,
            'product_ids': [self.product.id, premium_product.id]
        }
        response = self.client.post('/api/calculator/compare-products/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Check first product results
        standard_result = next(result for result in response.data if result['product_name'] == 'Standard Loan')
        premium_result = next(result for result in response.data if result['product_name'] == 'Premium Loan')
        
        self.assertAlmostEqual(standard_result['monthly_payment'], 1703.37, places=2)
        self.assertAlmostEqual(standard_result['total_fees'], 3500, places=2)
        
        self.assertAlmostEqual(premium_result['monthly_payment'], 1520.06, places=2)
        self.assertAlmostEqual(premium_result['total_fees'], 5250, places=2)  # 750 + (1.5% of 300000)
        
    def test_calculate_affordability(self):
        """Test that calculating affordability works correctly."""
        data = {
            'monthly_income': 10000,
            'monthly_debts': 2000,
            'down_payment': 60000,
            'interest_rate': 5.5,
            'term_months': 360,
            'debt_to_income_ratio': 0.36  # 36% DTI
        }
        response = self.client.post('/api/calculator/affordability/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('max_loan_amount', response.data)
        self.assertIn('max_purchase_price', response.data)
        self.assertIn('monthly_payment', response.data)
        
        # Verify calculations
        # Max monthly payment = (Monthly income * DTI) - Monthly debts
        # Max monthly payment = (10000 * 0.36) - 2000 = 1600
        # Using this payment to back-calculate the loan amount
        self.assertAlmostEqual(response.data['monthly_payment'], 1600, places=2)
        self.assertGreater(response.data['max_loan_amount'], 0)
        self.assertEqual(response.data['max_purchase_price'], 
                         response.data['max_loan_amount'] + data['down_payment'])
