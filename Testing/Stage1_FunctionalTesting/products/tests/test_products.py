from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from products.models import Product, Fee

User = get_user_model()

class ProductAPITestCase(TestCase):
    """Test case for the product API endpoints."""
    
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
        self.fee = Fee.objects.create(
            product=self.product,
            name='Application Fee',
            amount=500,
            is_percentage=False
        )
        self.client.force_authenticate(user=self.user)
        
    def test_list_products(self):
        """Test that the products list endpoint returns 200 and correct data structure."""
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)
        
    def test_retrieve_product(self):
        """Test that the product detail endpoint returns 200 and correct data."""
        response = self.client.get(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Standard Loan')
        self.assertEqual(response.data['interest_rate'], 5.5)
        self.assertEqual(response.data['term_months'], 360)
        
    def test_create_product(self):
        """Test that creating a product works correctly."""
        data = {
            'name': 'Premium Loan',
            'description': 'Premium mortgage with lower interest rate',
            'interest_rate': 4.5,
            'term_months': 360,
            'min_loan_amount': 100000,
            'max_loan_amount': 2000000,
            'min_credit_score': 700,
            'is_active': True
        }
        response = self.client.post('/api/products/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Premium Loan')
        self.assertEqual(response.data['interest_rate'], 4.5)
        self.assertEqual(Product.objects.count(), 2)
        
    def test_update_product(self):
        """Test that updating a product works correctly."""
        data = {
            'name': 'Standard Loan',
            'description': 'Standard fixed-rate mortgage loan',
            'interest_rate': 5.25,  # Updated interest rate
            'term_months': 360,
            'min_loan_amount': 50000,
            'max_loan_amount': 1200000,  # Updated max loan amount
            'min_credit_score': 650,
            'is_active': True
        }
        response = self.client.put(f'/api/products/{self.product.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['interest_rate'], 5.25)
        self.assertEqual(response.data['max_loan_amount'], 1200000)
        self.product.refresh_from_db()
        self.assertEqual(self.product.interest_rate, 5.25)
        self.assertEqual(self.product.max_loan_amount, 1200000)
        
    def test_partial_update_product(self):
        """Test that partially updating a product works correctly."""
        data = {
            'is_active': False  # Only update active status
        }
        response = self.client.patch(f'/api/products/{self.product.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_active'], False)
        self.product.refresh_from_db()
        self.assertEqual(self.product.is_active, False)
        
    def test_delete_product(self):
        """Test that deleting a product works correctly."""
        response = self.client.delete(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)
        
    def test_list_product_fees(self):
        """Test that listing product fees works correctly."""
        response = self.client.get(f'/api/products/{self.product.id}/fees/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Application Fee')
        self.assertEqual(response.data[0]['amount'], 500)
        
    def test_add_product_fee(self):
        """Test that adding a fee to a product works correctly."""
        data = {
            'name': 'Processing Fee',
            'amount': 2.5,
            'is_percentage': True
        }
        response = self.client.post(f'/api/products/{self.product.id}/fees/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Processing Fee')
        self.assertEqual(response.data['amount'], 2.5)
        self.assertEqual(response.data['is_percentage'], True)
        self.assertEqual(Fee.objects.count(), 2)
        
    def test_filter_products_by_interest_rate(self):
        """Test that filtering products by interest rate works correctly."""
        # Create additional products for filter testing
        Product.objects.create(
            name='Low Rate Loan',
            description='Low interest rate mortgage',
            interest_rate=3.5,
            term_months=360,
            min_loan_amount=100000,
            max_loan_amount=1500000,
            min_credit_score=720,
            is_active=True
        )
        Product.objects.create(
            name='High Rate Loan',
            description='High interest rate mortgage',
            interest_rate=7.5,
            term_months=360,
            min_loan_amount=25000,
            max_loan_amount=500000,
            min_credit_score=600,
            is_active=True
        )
        
        # Filter by maximum interest rate
        response = self.client.get('/api/products/?max_interest_rate=6.0')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        
        # Filter by minimum interest rate
        response = self.client.get('/api/products/?min_interest_rate=6.0')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'High Rate Loan')
        
    def test_filter_products_by_loan_amount(self):
        """Test that filtering products by loan amount works correctly."""
        # Create additional products for filter testing
        Product.objects.create(
            name='Small Loan',
            description='Small loan amount mortgage',
            interest_rate=6.0,
            term_months=180,
            min_loan_amount=10000,
            max_loan_amount=100000,
            min_credit_score=600,
            is_active=True
        )
        Product.objects.create(
            name='Jumbo Loan',
            description='Jumbo loan amount mortgage',
            interest_rate=6.5,
            term_months=360,
            min_loan_amount=500000,
            max_loan_amount=5000000,
            min_credit_score=740,
            is_active=True
        )
        
        # Filter by loan amount
        response = self.client.get('/api/products/?loan_amount=750000')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)  # Standard Loan and Jumbo Loan
        
        # Filter by loan amount and credit score
        response = self.client.get('/api/products/?loan_amount=750000&credit_score=730')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)  # Only Standard Loan
