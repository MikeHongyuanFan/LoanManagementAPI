from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from documents.models import Document, DocumentCategory

User = get_user_model()

class DocumentAPITestCase(TestCase):
    """Test case for the document API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.category = DocumentCategory.objects.create(
            name='Test Category',
            description='Test category description'
        )
        self.document = Document.objects.create(
            title='Test Document',
            description='Test description',
            uploaded_by=self.user,
            document_type='other',
            status='draft',
            category=self.category
        )
        self.client.force_authenticate(user=self.user)
        
    def test_list_documents(self):
        """Test that the documents list endpoint returns 200 and correct data structure."""
        response = self.client.get('/api/document-management/documents/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)
        
    def test_retrieve_document(self):
        """Test that the document detail endpoint returns 200 and correct data."""
        response = self.client.get(f'/api/document-management/documents/{self.document.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Document')
        self.assertEqual(response.data['description'], 'Test description')
        
    def test_create_document(self):
        """Test that creating a document works correctly."""
        data = {
            'title': 'New Document',
            'description': 'New description',
            'document_type': 'other',
            'status': 'draft',
            'category': self.category.id,
            'tags': []
        }
        response = self.client.post('/api/document-management/documents/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Document')
        self.assertEqual(Document.objects.count(), 2)
        
    def test_update_document(self):
        """Test that updating a document works correctly."""
        data = {
            'title': 'Updated Document',
            'description': 'Updated description',
            'document_type': 'other',
            'status': 'draft',
            'category': self.category.id,
            'tags': []
        }
        response = self.client.put(
            f'/api/document-management/documents/{self.document.id}/', 
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Document')
        self.document.refresh_from_db()
        self.assertEqual(self.document.title, 'Updated Document')
        
    def test_delete_document(self):
        """Test that deleting a document works correctly."""
        response = self.client.delete(f'/api/document-management/documents/{self.document.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Document.objects.count(), 0)
