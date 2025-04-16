import json
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from applications.models import Application
from borrowers.models import Borrower
from brokers.models import Broker
from products.models import Product
from documents.models import Document

User = get_user_model()

class BrokerApplicationIntegrationTest(TestCase):
    """
    Integration test for the broker and application relationship.
    Tests the interaction between brokers, applications, and related components.
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
    
    def test_broker_creation_and_retrieval(self):
        """
        Test creating a broker and retrieving it.
        """
        # Create a broker
        broker_data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com',
            'phone_number': '9876543210',
            'company_name': 'ABC Brokers',
            'license_number': 'BRK12345',
            'years_of_experience': 5
        }
        
        response = self.client.post(
            reverse('broker-list'),
            data=json.dumps(broker_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        broker_id = response.data['id']
        
        # Retrieve the broker
        response = self.client.get(
            reverse('broker-detail', kwargs={'pk': broker_id})
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Jane')
        self.assertEqual(response.data['last_name'], 'Smith')
        self.assertEqual(response.data['company_name'], 'ABC Brokers')
        self.assertEqual(response.data['license_number'], 'BRK12345')
        self.assertEqual(response.data['years_of_experience'], 5)
    
    def test_application_with_broker(self):
        """
        Test creating an application with a broker and verifying the relationship.
        """
        # Create a broker
        broker = Broker.objects.create(
            first_name='Jane',
            last_name='Smith',
            email='jane.smith@example.com',
            phone_number='9876543210',
            company_name='ABC Brokers',
            license_number='BRK12345',
            years_of_experience=5
        )
        
        # Create an application with the broker
        application_data = {
            'borrower': self.borrower.id,
            'broker': broker.id,
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
        
        # Retrieve the application
        response = self.client.get(
            reverse('application-detail', kwargs={'pk': application_id})
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if broker is returned as an object or just an ID
        if isinstance(response.data['broker'], dict):
            self.assertEqual(response.data['broker']['id'], broker.id)
        else:
            self.assertEqual(response.data['broker'], broker.id)
        
        # Verify the relationship in the database
        application = Application.objects.get(id=application_id)
        self.assertEqual(application.broker, broker)
    
    def test_applications_by_broker(self):
        """
        Test retrieving applications by broker.
        """
        # Create two brokers
        broker1 = Broker.objects.create(
            first_name='Jane',
            last_name='Smith',
            email='jane.smith@example.com',
            phone_number='9876543210',
            company_name='ABC Brokers',
            license_number='BRK12345',
            years_of_experience=5
        )
        
        broker2 = Broker.objects.create(
            first_name='Robert',
            last_name='Johnson',
            email='robert.johnson@example.com',
            phone_number='5551234567',
            company_name='XYZ Brokers',
            license_number='BRK67890',
            years_of_experience=8
        )
        
        # Create applications for broker1
        application1 = Application.objects.create(
            borrower=self.borrower,
            broker=broker1,
            product=self.product,
            gross_loan_amount=300000.00,
            net_loan_amount=297000.00,
            status='draft',
            stage='application'
        )
        
        application2 = Application.objects.create(
            borrower=self.borrower,
            broker=broker1,
            product=self.product,
            gross_loan_amount=250000.00,
            net_loan_amount=247500.00,
            status='draft',
            stage='application'
        )
        
        # Create application for broker2
        application3 = Application.objects.create(
            borrower=self.borrower,
            broker=broker2,
            product=self.product,
            gross_loan_amount=200000.00,
            net_loan_amount=198000.00,
            status='draft',
            stage='application'
        )
        
        # Get applications for broker1
        response = self.client.get(
            f"{reverse('application-list')}?broker={broker1.id}"
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify that only broker1's applications are returned
        applications_data = response.data
        if isinstance(applications_data, list):
            self.assertEqual(len(applications_data), 2)
            application_ids = [app['id'] for app in applications_data]
            self.assertIn(application1.id, application_ids)
            self.assertIn(application2.id, application_ids)
            self.assertNotIn(application3.id, application_ids)
        
        # Get applications for broker2
        response = self.client.get(
            f"{reverse('application-list')}?broker={broker2.id}"
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify that only broker2's applications are returned
        applications_data = response.data
        if isinstance(applications_data, list):
            self.assertEqual(len(applications_data), 1)
            self.assertEqual(applications_data[0]['id'], application3.id)
    
    def test_update_broker_for_application(self):
        """
        Test updating the broker for an application.
        """
        # Create two brokers
        broker1 = Broker.objects.create(
            first_name='Jane',
            last_name='Smith',
            email='jane.smith@example.com',
            phone_number='9876543210',
            company_name='ABC Brokers',
            license_number='BRK12345',
            years_of_experience=5
        )
        
        broker2 = Broker.objects.create(
            first_name='Robert',
            last_name='Johnson',
            email='robert.johnson@example.com',
            phone_number='5551234567',
            company_name='XYZ Brokers',
            license_number='BRK67890',
            years_of_experience=8
        )
        
        # Create application with broker1
        application = Application.objects.create(
            borrower=self.borrower,
            broker=broker1,
            product=self.product,
            gross_loan_amount=300000.00,
            net_loan_amount=297000.00,
            status='draft',
            stage='application'
        )
        
        # Update application to use broker2
        update_data = {
            'broker': broker2.id
        }
        
        response = self.client.patch(
            reverse('application-detail', kwargs={'pk': application.id}),
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if broker is returned as an object or just an ID
        if isinstance(response.data['broker'], dict):
            self.assertEqual(response.data['broker']['id'], broker2.id)
        else:
            self.assertEqual(response.data['broker'], broker2.id)
        
        # Verify the update in the database
        updated_application = Application.objects.get(id=application.id)
        self.assertEqual(updated_application.broker, broker2)
    
    def test_broker_update(self):
        """
        Test updating broker information.
        """
        # Create a broker
        broker = Broker.objects.create(
            first_name='Jane',
            last_name='Smith',
            email='jane.smith@example.com',
            phone_number='9876543210',
            company_name='ABC Brokers',
            license_number='BRK12345',
            years_of_experience=5
        )
        
        # Update broker information
        update_data = {
            'company_name': 'Smith Brokers LLC',
            'phone_number': '5559876543',
            'years_of_experience': 7
        }
        
        response = self.client.patch(
            reverse('broker-detail', kwargs={'pk': broker.id}),
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company_name'], 'Smith Brokers LLC')
        self.assertEqual(response.data['phone_number'], '5559876543')
        self.assertEqual(response.data['years_of_experience'], 7)
        
        # Verify the update in the database
        updated_broker = Broker.objects.get(id=broker.id)
        self.assertEqual(updated_broker.company_name, 'Smith Brokers LLC')
        self.assertEqual(updated_broker.phone_number, '5559876543')
        self.assertEqual(updated_broker.years_of_experience, 7)
        
        # Verify that other fields were not changed
        self.assertEqual(updated_broker.first_name, 'Jane')
        self.assertEqual(updated_broker.last_name, 'Smith')
        self.assertEqual(updated_broker.email, 'jane.smith@example.com')
        self.assertEqual(updated_broker.license_number, 'BRK12345')
