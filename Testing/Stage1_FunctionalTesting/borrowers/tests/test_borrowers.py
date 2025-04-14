from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from borrowers.models import Borrower

User = get_user_model()

class BorrowerAPITestCase(TestCase):
    """Test case for the borrower API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.borrower = Borrower.objects.create(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone_number='1234567890',
            address='123 Main St',
            city='Anytown',
            state='CA',
            zip_code='12345'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_list_borrowers(self):
        """Test that the borrowers list endpoint returns 200 and correct data structure."""
        response = self.client.get('/api/borrowers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)
        
    def test_retrieve_borrower(self):
        """Test that the borrower detail endpoint returns 200 and correct data."""
        response = self.client.get(f'/api/borrowers/{self.borrower.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'John')
        self.assertEqual(response.data['last_name'], 'Doe')
        self.assertEqual(response.data['email'], 'john.doe@example.com')
        
    def test_create_borrower(self):
        """Test that creating a borrower works correctly."""
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com',
            'phone_number': '0987654321',
            'address': '456 Oak St',
            'city': 'Othertown',
            'state': 'NY',
            'zip_code': '54321'
        }
        response = self.client.post('/api/borrowers/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['first_name'], 'Jane')
        self.assertEqual(response.data['last_name'], 'Smith')
        self.assertEqual(Borrower.objects.count(), 2)
        
    def test_update_borrower(self):
        """Test that updating a borrower works correctly."""
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone_number': '1234567890',
            'address': '789 Pine St',  # Updated address
            'city': 'Newtown',  # Updated city
            'state': 'CA',
            'zip_code': '12345'
        }
        response = self.client.put(f'/api/borrowers/{self.borrower.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['address'], '789 Pine St')
        self.assertEqual(response.data['city'], 'Newtown')
        self.borrower.refresh_from_db()
        self.assertEqual(self.borrower.address, '789 Pine St')
        self.assertEqual(self.borrower.city, 'Newtown')
        
    def test_partial_update_borrower(self):
        """Test that partially updating a borrower works correctly."""
        data = {
            'phone_number': '5555555555'  # Only update phone number
        }
        response = self.client.patch(f'/api/borrowers/{self.borrower.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone_number'], '5555555555')
        self.borrower.refresh_from_db()
        self.assertEqual(self.borrower.phone_number, '5555555555')
        
    def test_delete_borrower(self):
        """Test that deleting a borrower works correctly."""
        response = self.client.delete(f'/api/borrowers/{self.borrower.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Borrower.objects.count(), 0)
        
    def test_search_borrowers(self):
        """Test that searching borrowers works correctly."""
        # Create additional borrowers for search testing
        Borrower.objects.create(
            first_name='Jane',
            last_name='Doe',
            email='jane.doe@example.com',
            phone_number='0987654321',
            address='456 Oak St',
            city='Anytown',
            state='CA',
            zip_code='12345'
        )
        Borrower.objects.create(
            first_name='Bob',
            last_name='Smith',
            email='bob.smith@example.com',
            phone_number='1122334455',
            address='789 Elm St',
            city='Othertown',
            state='NY',
            zip_code='54321'
        )
        
        # Search by last name
        response = self.client.get('/api/borrowers/?search=Doe')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        
        # Search by city
        response = self.client.get('/api/borrowers/?search=Othertown')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['first_name'], 'Bob')
        
    def test_filter_borrowers_by_state(self):
        """Test that filtering borrowers by state works correctly."""
        # Create additional borrowers for filter testing
        Borrower.objects.create(
            first_name='Jane',
            last_name='Doe',
            email='jane.doe@example.com',
            phone_number='0987654321',
            address='456 Oak St',
            city='Anytown',
            state='CA',
            zip_code='12345'
        )
        Borrower.objects.create(
            first_name='Bob',
            last_name='Smith',
            email='bob.smith@example.com',
            phone_number='1122334455',
            address='789 Elm St',
            city='Othertown',
            state='NY',
            zip_code='54321'
        )
        
        # Filter by CA state
        response = self.client.get('/api/borrowers/?state=CA')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        
        # Filter by NY state
        response = self.client.get('/api/borrowers/?state=NY')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['first_name'], 'Bob')
