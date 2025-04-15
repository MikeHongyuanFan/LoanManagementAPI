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
from calculator.models import LoanCalculation, Fee, ApplicationFee
from documents.models import Document, DocumentApproval

User = get_user_model()

class LoanApplicationWorkflowTest(TestCase):
    """
    Integration test for the complete loan application workflow.
    Tests the interaction between multiple components in a real-world scenario.
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
        self.approver_user = User.objects.create_user(
            username='approver_user',
            email='approver@example.com',
            password='password123',
            is_staff=True
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
        
        # Create test product
        self.product = Product.objects.create(
            name='Standard Loan',
            description='Standard loan product',
            interest_rate=5.5,
            term_months=360,
            min_amount=10000,
            max_amount=500000
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
        
        # Associate fees with product
        self.product.calculator_fees.add(self.application_fee, self.establishment_fee)
        
        # Set up API client
        self.client = APIClient()
    
    def test_complete_loan_application_workflow(self):
        """
        Test the complete loan application workflow from submission to approval.
        This tests the integration between multiple components:
        1. Application creation
        2. Document upload and association
        3. Loan calculation
        4. Fee calculation
        5. Document approval workflow
        6. Application status updates
        """
        # Step 1: Authenticate as borrower and create application
        self.client.force_authenticate(user=self.borrower_user)
        
        application_data = {
            'borrower': self.borrower.id,
            'product': self.product.id,
            'loan_amount': 300000.00,
            'purpose': 'Home purchase',
            'property_address': '123 Main St, Anytown, USA',
            'property_value': 375000.00
        }
        
        response = self.client.post(
            reverse('application-list'),
            data=json.dumps(application_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        application_id = response.data['id']
        
        # Step 2: Upload document for the application
        document_data = {
            'title': 'Income Verification',
            'description': 'Proof of income',
            'document_type': 'income_verification',
            'application': application_id
        }
        
        response = self.client.post(
            reverse('document-list'),
            data=document_data,
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        document_id = response.data['id']
        
        # Step 3: Calculate loan details
        calculation_data = {
            'application_id': application_id,
            'loan_amount': 300000.00,
            'interest_rate': 5.5,
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
        
        # Step 4: Authenticate as staff and request document approval
        self.client.force_authenticate(user=self.staff_user)
        
        approval_data = {
            'document': document_id,
            'reviewer': self.approver_user.id,
            'comments': 'Please review this income verification document'
        }
        
        response = self.client.post(
            reverse('document-request-approval', kwargs={'pk': document_id}),
            data=json.dumps(approval_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        approval_id = response.data['id']
        
        # Step 5: Authenticate as approver and approve document
        self.client.force_authenticate(user=self.approver_user)
        
        response = self.client.post(
            reverse('documentapproval-approve', kwargs={'pk': approval_id}),
            data=json.dumps({'comments': 'Document looks good'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 6: Authenticate as staff and update application status
        self.client.force_authenticate(user=self.staff_user)
        
        status_update_data = {
            'status': 'approved',
            'notes': 'Application approved based on verified documents and calculations'
        }
        
        response = self.client.patch(
            reverse('application-detail', kwargs={'pk': application_id}),
            data=json.dumps(status_update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'approved')
        
        # Step 7: Verify the final state of all components
        
        # Check application status
        application = Application.objects.get(id=application_id)
        self.assertEqual(application.status, 'approved')
        
        # Check document approval status
        document = Document.objects.get(id=document_id)
        approval = DocumentApproval.objects.get(document=document)
        self.assertEqual(approval.status, 'approved')
        
        # Check loan calculation exists
        calculation = LoanCalculation.objects.get(application=application)
        self.assertIsNotNone(calculation)
        self.assertEqual(calculation.loan_amount, Decimal('300000.00'))
        self.assertEqual(calculation.interest_rate, Decimal('5.5'))
        
        # Check fees were calculated
        application_fees = ApplicationFee.objects.filter(application=application)
        self.assertEqual(application_fees.count(), 2)
        
        # Verify fee amounts
        fee_amounts = {fee.fee.name: fee.calculated_amount for fee in application_fees}
        self.assertEqual(fee_amounts['Application Fee'], Decimal('500.00'))
        self.assertEqual(fee_amounts['Establishment Fee'], Decimal('3000.00'))  # 1% of 300000
        
        # Verify relationships between components
        self.assertEqual(calculation.product, self.product)
        self.assertEqual(document.application, application)
        self.assertEqual(application.borrower, self.borrower)
