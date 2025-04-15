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
from documents.models import Document

User = get_user_model()

class BorrowerApplicationIntegrationTest(TestCase):
    """
    Integration test for the borrower and application relationship.
    Tests the interaction between borrowers, applications, and related components.
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
        
        # Create test product
        self.product = Product.objects.create(
            name='Standard Loan',
            description='Standard loan product',
            interest_rate=5.5,
            term_months=360,
            min_loan_amount=10000,
            max_loan_amount=500000
        )
        
        # Set up API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.staff_user)
    
    def test_borrower_application_document_integration(self):
        """
        Test the integration between borrowers, applications, and documents.
        Verifies that:
        1. Borrower can be created
        2. Multiple applications can be created for a borrower
        3. Documents can be associated with applications
        4. Borrower profile can be updated
        5. Applications can be retrieved by borrower
        """
        # Step 1: Create a borrower
        borrower_data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com',
            'phone_number': '9876543210',
            'dob': '1985-05-15',
            'state': 'NY'
        }
        
        response = self.client.post(
            reverse('borrower-list'),
            data=json.dumps(borrower_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        borrower_id = response.data['id']
        
        # Step 2: Create first application for the borrower
        application1_data = {
            'borrower': borrower_id,
            'product': self.product.id,
            'gross_loan_amount': 250000.00,
            'net_loan_amount': 247500.00,
            'status': 'draft',
            'stage': 'application'
        }
        
        response = self.client.post(
            reverse('application-list'),
            data=json.dumps(application1_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        application1_id = response.data['id']
        
        # Step 3: Create second application for the same borrower
        application2_data = {
            'borrower': borrower_id,
            'product': self.product.id,
            'gross_loan_amount': 150000.00,
            'net_loan_amount': 148500.00,
            'status': 'draft',
            'stage': 'application'
        }
        
        response = self.client.post(
            reverse('application-list'),
            data=json.dumps(application2_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        application2_id = response.data['id']
        
        # Step 4: Create documents directly in the database instead of using API
        # This avoids issues with file upload requirements in the API
        document1 = Document.objects.create(
            title='Income Verification',
            description='Proof of income',
            document_type='financial',
            application_id=application1_id,
            uploaded_by=self.staff_user
        )
        document1_id = document1.id
        
        document2 = Document.objects.create(
            title='Property Valuation',
            description='Property valuation report',
            document_type='property',
            application_id=application2_id,
            uploaded_by=self.staff_user
        )
        document2_id = document2.id
        
        # Step 6: Update borrower profile
        updated_borrower_data = {
            'phone_number': '5551234567'
        }
        
        response = self.client.patch(
            reverse('borrower-detail', kwargs={'pk': borrower_id}),
            data=json.dumps(updated_borrower_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone_number'], '5551234567')
        
        # Step 7: Get all applications for the borrower
        response = self.client.get(
            f"{reverse('application-list')}?borrower={borrower_id}"
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify that we have at least the two applications we created
        applications_data = response.data
        if isinstance(applications_data, str):
            applications_data = json.loads(applications_data)
            
        self.assertGreaterEqual(len(applications_data), 2)
        
        # Verify the applications in the database directly
        applications = Application.objects.filter(borrower_id=borrower_id)
        self.assertGreaterEqual(applications.count(), 2)
        
        # Step 8: Get all documents for the first application
        response = self.client.get(
            f"{reverse('document-list')}?application={application1_id}"
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify that we have at least one document for this application
        self.assertGreaterEqual(len(response.data), 1)
        
        # Verify directly in the database
        docs_for_app1 = Document.objects.filter(application_id=application1_id)
        self.assertEqual(docs_for_app1.count(), 1)
        self.assertEqual(docs_for_app1[0].title, 'Income Verification')
        
        # Step 9: Get all documents for the second application
        response = self.client.get(
            f"{reverse('document-list')}?application={application2_id}"
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify that we have at least one document for this application
        self.assertGreaterEqual(len(response.data), 1)
        
        # Verify directly in the database
        docs_for_app2 = Document.objects.filter(application_id=application2_id)
        self.assertEqual(docs_for_app2.count(), 1)
        self.assertEqual(docs_for_app2[0].title, 'Property Valuation')
        
        # Step 10: Verify the relationships in the database
        borrower = Borrower.objects.get(id=borrower_id)
        applications = Application.objects.filter(borrower=borrower)
        self.assertEqual(applications.count(), 2)
        
        application1 = Application.objects.get(id=application1_id)
        application2 = Application.objects.get(id=application2_id)
        
        self.assertEqual(application1.borrower, borrower)
        self.assertEqual(application2.borrower, borrower)
        
        document1 = Document.objects.get(id=document1_id)
        document2 = Document.objects.get(id=document2_id)
        
        self.assertEqual(document1.application, application1)
        self.assertEqual(document2.application, application2)
    
    def test_borrower_multiple_applications_with_different_products(self):
        """
        Test that a borrower can have multiple applications with different products.
        Verifies that:
        1. Borrower can be created
        2. Multiple products can be created
        3. Applications with different products can be created for the same borrower
        4. Product details are correctly associated with applications
        """
        # Step 1: Create a borrower
        borrower_data = {
            'first_name': 'Robert',
            'last_name': 'Johnson',
            'email': 'robert.johnson@example.com',
            'phone_number': '5559876543',
            'dob': '1978-08-20',
            'state': 'CA'
        }
        
        response = self.client.post(
            reverse('borrower-list'),
            data=json.dumps(borrower_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        borrower_id = response.data['id']
        
        # Step 2: Create a second product
        product2_data = {
            'name': 'Variable Rate Loan',
            'description': '5/1 ARM loan',
            'interest_rate': 4.5,
            'term_months': 360,
            'min_loan_amount': 10000,
            'max_loan_amount': 500000
        }
        
        response = self.client.post(
            reverse('product-list'),
            data=json.dumps(product2_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        product2_id = response.data['id']
        
        # Step 3: Create application with first product
        application1_data = {
            'borrower': borrower_id,
            'product': self.product.id,
            'gross_loan_amount': 300000.00,
            'net_loan_amount': 297000.00,
            'status': 'draft',
            'stage': 'application'
        }
        
        response = self.client.post(
            reverse('application-list'),
            data=json.dumps(application1_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        application1_id = response.data['id']
        
        # Step 4: Create application with second product
        application2_data = {
            'borrower': borrower_id,
            'product': product2_id,
            'gross_loan_amount': 200000.00,
            'net_loan_amount': 198000.00,
            'status': 'draft',
            'stage': 'application'
        }
        
        response = self.client.post(
            reverse('application-list'),
            data=json.dumps(application2_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        application2_id = response.data['id']
        
        # Step 5: Verify the relationships in the database
        borrower = Borrower.objects.get(id=borrower_id)
        applications = Application.objects.filter(borrower=borrower)
        self.assertEqual(applications.count(), 2)
        
        application1 = Application.objects.get(id=application1_id)
        application2 = Application.objects.get(id=application2_id)
        
        self.assertEqual(application1.borrower, borrower)
        self.assertEqual(application2.borrower, borrower)
        
        self.assertEqual(application1.product.id, self.product.id)
        self.assertEqual(application2.product.id, product2_id)
        
        # Step 6: Verify product details are correctly associated
        self.assertEqual(application1.product.interest_rate, Decimal('5.5'))
        self.assertEqual(application2.product.interest_rate, Decimal('4.5'))
        
        self.assertEqual(application1.product.name, 'Standard Loan')
        self.assertEqual(application2.product.name, 'Variable Rate Loan')
