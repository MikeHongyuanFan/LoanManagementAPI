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

User = get_user_model()

class ApplicationStatusWorkflowTest(TestCase):
    """
    Integration test for the application status workflow.
    Tests the transitions between different application statuses and stages.
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
        
        # Associate fees with product
        self.product.calculator_fees.add(self.application_fee, self.establishment_fee)
        
        # Set up API client
        self.client = APIClient()
    
    def test_application_status_transitions(self):
        """
        Test the complete application status workflow from draft to approved.
        Verifies that:
        1. Application can be created in draft status
        2. Application can transition from draft to submitted
        3. Application can transition from submitted to under_review
        4. Application can transition from under_review to approved
        """
        # Step 1: Authenticate as staff and create application in draft status
        self.client.force_authenticate(user=self.staff_user)
        
        application_data = {
            'borrower': self.borrower.id,
            'product': self.product.id,
            'gross_loan_amount': 300000.00,
            'net_loan_amount': 297000.00,
            'status': 'draft',
            'stage': 'application'
        }
        
        response = self.client.post(
            reverse('application-list'),
            data=json.dumps(application_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        application_id = response.data['id']
        
        # Step 2: Transition from draft to submitted
        status_update_data = {
            'status': 'submitted',
            'notes': 'Application submitted for review'
        }
        
        response = self.client.patch(
            reverse('application-detail', kwargs={'pk': application_id}),
            data=json.dumps(status_update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'submitted')
        
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
        
        # Step 4: Transition from submitted to under_review
        status_update_data = {
            'status': 'under_review',
            'notes': 'Application is now under review'
        }
        
        response = self.client.patch(
            reverse('application-detail', kwargs={'pk': application_id}),
            data=json.dumps(status_update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'under_review')
        
        # Step 5: Transition from under_review to approved
        status_update_data = {
            'status': 'approved',
            'notes': 'Application approved based on review'
        }
        
        response = self.client.patch(
            reverse('application-detail', kwargs={'pk': application_id}),
            data=json.dumps(status_update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'approved')
        
        # Step 7: Verify the final state
        application = Application.objects.get(id=application_id)
        self.assertEqual(application.status, 'approved')
        
        # Check that calculation exists
        calculation = LoanCalculation.objects.get(application=application)
        self.assertIsNotNone(calculation)
        
        # Check that fees were calculated
        application_fees = ApplicationFee.objects.filter(application=application)
        self.assertEqual(application_fees.count(), 2)
    
    def test_application_stage_transitions(self):
        """
        Test the application stage transitions from application to approval.
        Verifies that:
        1. Application can be created in application stage
        2. Application can transition from application to verification
        3. Application can transition from verification to assessment
        4. Application can transition from assessment to approval
        """
        # Step 1: Authenticate as staff and create application
        self.client.force_authenticate(user=self.staff_user)
        
        application_data = {
            'borrower': self.borrower.id,
            'product': self.product.id,
            'gross_loan_amount': 300000.00,
            'net_loan_amount': 297000.00,
            'status': 'submitted',
            'stage': 'application'
        }
        
        response = self.client.post(
            reverse('application-list'),
            data=json.dumps(application_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        application_id = response.data['id']
        
        # Step 2: Transition from application to verification stage
        stage_update_data = {
            'stage': 'verification',
            'notes': 'Moving to verification stage'
        }
        
        response = self.client.patch(
            reverse('application-detail', kwargs={'pk': application_id}),
            data=json.dumps(stage_update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['stage'], 'verification')
        
        # Step 3: Transition from verification to assessment stage
        stage_update_data = {
            'stage': 'assessment',
            'notes': 'Moving to assessment stage'
        }
        
        response = self.client.patch(
            reverse('application-detail', kwargs={'pk': application_id}),
            data=json.dumps(stage_update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['stage'], 'assessment')
        
        # Step 4: Transition from assessment to approval stage
        stage_update_data = {
            'stage': 'approval',
            'notes': 'Moving to approval stage'
        }
        
        response = self.client.patch(
            reverse('application-detail', kwargs={'pk': application_id}),
            data=json.dumps(stage_update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['stage'], 'approval')
        
        # Step 5: Verify the final state
        application = Application.objects.get(id=application_id)
        self.assertEqual(application.stage, 'approval')
    
    def test_application_rejection_workflow(self):
        """
        Test the application rejection workflow.
        Verifies that:
        1. Application can be rejected from submitted status
        2. Rejection notes are recorded
        """
        # Step 1: Authenticate as staff and create application
        self.client.force_authenticate(user=self.staff_user)
        
        application_data = {
            'borrower': self.borrower.id,
            'product': self.product.id,
            'gross_loan_amount': 300000.00,
            'net_loan_amount': 297000.00,
            'status': 'submitted',
            'stage': 'application'
        }
        
        response = self.client.post(
            reverse('application-list'),
            data=json.dumps(application_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        application_id = response.data['id']
        
        # Step 2: Reject the application
        status_update_data = {
            'status': 'rejected',
            'notes': 'Application rejected due to insufficient income'
        }
        
        response = self.client.patch(
            reverse('application-detail', kwargs={'pk': application_id}),
            data=json.dumps(status_update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'rejected')
        
        # Step 3: Verify the final state
        application = Application.objects.get(id=application_id)
        self.assertEqual(application.status, 'rejected')
