from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from documents.models import Document

User = get_user_model()

class DocumentInputValidationTestCase(TestCase):
    """Test case for document API input validation."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_create_document_missing_required_field(self):
        """Test that creating a document without a required field returns 400."""
        data = {
            'description': 'Test document'
            # Missing required 'title' field
        }
        response = self.client.post('/api/document-management/documents/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)  # Error message for missing field
        
    def test_create_document_invalid_field_type(self):
        """Test that creating a document with invalid field type returns 400."""
        data = {
            'title': 'Test Document',
            'description': 123  # Should be string
        }
        response = self.client.post('/api/document-management/documents/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('description', response.data)
        
    def test_create_document_title_too_long(self):
        """Test that creating a document with too long title returns 400."""
        data = {
            'title': 'A' * 256,  # Assuming max length is 255
            'description': 'Test description'
        }
        response = self.client.post('/api/document-management/documents/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
        
    def test_update_document_invalid_id(self):
        """Test that updating a non-existent document returns 404."""
        data = {
            'title': 'Updated Document',
            'description': 'Updated description'
        }
        response = self.client.put('/api/document-management/documents/999/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_create_document_invalid_json(self):
        """Test that sending invalid JSON returns 400."""
        response = self.client.post(
            '/api/document-management/documents/',
            data='{invalid json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_create_document_with_invalid_enum_value(self):
        """Test that creating a document with invalid enum value returns 400."""
        data = {
            'title': 'Test Document',
            'description': 'Test description',
            'status': 'invalid_status'  # Assuming this is an enum field
        }
        response = self.client.post('/api/document-management/documents/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('status', response.data)
