import json
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from applications.models import Application
from borrowers.models import Borrower
from products.models import Product
from calculator.models import LoanCalculation, Fee, ApplicationFee, RepaymentSchedule

User = get_user_model()

class CalculatorIntegrationTest(TestCase):
    """
    Integration test for the loan calculator components.
    Tests the interaction between calculator, fees, products, and applications.
    """
    
    def setUp(self):
        # Create test users
        self.staff_user = User.objects.create_user(
            username='staff_user',
            email='staff@example.com',
            password='password123',
            is_staff=True
        )
        self.borrower_user = User.objects.create_user(
            username='borrower_user',
            email='borrower@example.com',
            password='password123'
        )
        
        # Create test borrower
        self.borrower = Borrower.objects.create(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone_number='1234567890',
            dob='1980-01-01',
            state='CA'
        )
        
        # Create test products
        self.fixed_rate_product = Product.objects.create(
            name='Fixed Rate Loan',
            description='30-year fixed rate loan',
            interest_rate=5.5,
            term_months=360,
            min_loan_amount=10000,
            max_loan_amount=500000
        )
        
        self.variable_rate_product = Product.objects.create(
            name='Variable Rate Loan',
            description='5/1 ARM loan',
            interest_rate=4.5,
            term_months=360,
            min_loan_amount=10000,
            max_loan_amount=500000
        )
        
        # Create test fees
        self.application_fee = Fee.objects.create(
            name='Application Fee',
            description='Fee for processing application',
            fee_type='application',
            calculation_method='fixed',
            amount=500.00,
            is_active=True
        )
        
        self.establishment_fee = Fee.objects.create(
            name='Establishment Fee',
            description='Fee for establishing loan',
            fee_type='establishment',
            calculation_method='percentage',
            amount=1.00,  # 1% of loan amount
            is_active=True
        )
        
        self.early_repayment_fee = Fee.objects.create(
            name='Early Repayment Fee',
            description='Fee for early repayment',
            fee_type='early_repayment',
            calculation_method='percentage',
            amount=2.00,  # 2% of remaining balance
            is_active=True
        )
        
        # Associate fees with products
        self.fixed_rate_product.calculator_fees.add(self.application_fee, self.establishment_fee)
        self.variable_rate_product.calculator_fees.add(self.application_fee, self.establishment_fee, self.early_repayment_fee)
        
        # Create test applications
        self.fixed_rate_application = Application.objects.create(
            borrower=self.borrower,
            product=self.fixed_rate_product,
            gross_loan_amount=300000.00,
            net_loan_amount=297000.00,
            status='in_progress'
        )
        
        self.variable_rate_application = Application.objects.create(
            borrower=self.borrower,
            product=self.variable_rate_product,
            gross_loan_amount=250000.00,
            net_loan_amount=247500.00,
            status='in_progress'
        )
        
        # Set up API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.staff_user)
    
    def test_calculator_product_fee_integration(self):
        """
        Test the integration between calculator, products, and fees.
        Verifies that:
        1. Calculator uses product parameters correctly
        2. Fees are calculated based on product and loan amount
        3. Repayment schedule is generated correctly
        4. All relationships are maintained properly
        """
        # Step 1: Calculate loan details for fixed rate product
        calculation_data = {
            'application_id': self.fixed_rate_application.id,
            'loan_amount': 300000.00,
            'interest_rate': 5.5,  # Same as product rate
            'loan_term_years': 30,
            'interest_type': 'fixed',
            'compounding_period': 'monthly'
        }
        
        response = self.client.post(
            reverse('loancalculation-calculate'),
            data=json.dumps(calculation_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('monthly_payment', response.data)
        self.assertIn('total_payments', response.data)
        self.assertIn('total_interest', response.data)
        self.assertIn('fees', response.data)
        
        # Step 2: Verify calculation results
        calculation_id = response.data['id']
        calculation = LoanCalculation.objects.get(id=calculation_id)
        
        # Check basic calculation fields
        self.assertEqual(calculation.loan_amount, Decimal('300000.00'))
        self.assertEqual(calculation.interest_rate, Decimal('5.5'))
        self.assertEqual(calculation.loan_term_years, 30)
        self.assertEqual(calculation.interest_type, 'fixed')
        
        # Check relationships
        self.assertEqual(calculation.application, self.fixed_rate_application)
        self.assertEqual(calculation.product, self.fixed_rate_product)
        
        # Step 3: Verify fees were calculated correctly
        application_fees = ApplicationFee.objects.filter(application=self.fixed_rate_application)
        self.assertEqual(application_fees.count(), 2)
        
        fee_amounts = {fee.fee.name: fee.calculated_amount for fee in application_fees}
        self.assertEqual(fee_amounts['Application Fee'], Decimal('500.00'))
        self.assertEqual(fee_amounts['Establishment Fee'], Decimal('3000.00'))  # 1% of 300000
        
        # Step 4: Verify repayment schedule was generated
        repayments = RepaymentSchedule.objects.filter(calculation=calculation)
        self.assertEqual(repayments.count(), 360)  # 30 years * 12 months
        
        # Check first payment
        first_payment = repayments.order_by('payment_number').first()
        self.assertEqual(first_payment.payment_number, 1)
        self.assertEqual(first_payment.payment_amount, calculation.monthly_payment)
        self.assertTrue(first_payment.interest_amount > 0)
        self.assertTrue(first_payment.principal_amount > 0)
        self.assertTrue(first_payment.remaining_balance < Decimal('300000.00'))
        
        # Check last payment
        last_payment = repayments.order_by('payment_number').last()
        self.assertEqual(last_payment.payment_number, 360)
        self.assertEqual(last_payment.remaining_balance, Decimal('0.00'))
        
        # Step 5: Calculate loan details for variable rate product
        calculation_data = {
            'application_id': self.variable_rate_application.id,
            'loan_amount': 250000.00,
            'interest_rate': 4.5,  # Same as product rate
            'loan_term_years': 30,
            'interest_type': 'variable',
            'compounding_period': 'monthly'
        }
        
        response = self.client.post(
            reverse('loancalculation-calculate'),
            data=json.dumps(calculation_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 6: Verify variable rate calculation results
        var_calculation_id = response.data['id']
        var_calculation = LoanCalculation.objects.get(id=var_calculation_id)
        
        # Check relationships
        self.assertEqual(var_calculation.application, self.variable_rate_application)
        self.assertEqual(var_calculation.product, self.variable_rate_product)
        
        # Step 7: Verify variable rate fees were calculated correctly
        var_application_fees = ApplicationFee.objects.filter(application=self.variable_rate_application)
        self.assertEqual(var_application_fees.count(), 3)  # Should include early repayment fee
        
        var_fee_amounts = {fee.fee.name: fee.calculated_amount for fee in var_application_fees}
        self.assertEqual(var_fee_amounts['Application Fee'], Decimal('500.00'))
        self.assertEqual(var_fee_amounts['Establishment Fee'], Decimal('2500.00'))  # 1% of 250000
        self.assertIn('Early Repayment Fee', var_fee_amounts)
        
        # Step 8: Compare calculations between products
        self.assertLess(var_calculation.monthly_payment, calculation.monthly_payment)
        self.assertLess(var_calculation.total_interest, calculation.total_interest)
        
        # Step 9: Test fee relationship with calculations
        for fee in application_fees:
            self.assertEqual(fee.calculation, calculation)
        
        for fee in var_application_fees:
            self.assertEqual(fee.calculation, var_calculation)
        
        # Step 10: Verify ManyToMany relationship between Fee and LoanCalculation
        fixed_rate_fees = list(calculation.fee_definitions.all())
        variable_rate_fees = list(var_calculation.fee_definitions.all())
        
        self.assertEqual(len(fixed_rate_fees), 2)
        self.assertEqual(len(variable_rate_fees), 3)
        
        # Check that the fees are correctly associated with calculations
        fixed_fee_names = [fee.name for fee in fixed_rate_fees]
        self.assertIn('Application Fee', fixed_fee_names)
        self.assertIn('Establishment Fee', fixed_fee_names)
        
        var_fee_names = [fee.name for fee in variable_rate_fees]
        self.assertIn('Application Fee', var_fee_names)
        self.assertIn('Establishment Fee', var_fee_names)
        self.assertIn('Early Repayment Fee', var_fee_names)
