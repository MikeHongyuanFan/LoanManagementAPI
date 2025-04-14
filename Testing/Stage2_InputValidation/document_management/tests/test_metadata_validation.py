from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from documents.models import Document, CustomMetadataField, DocumentMetadata
import json

User = get_user_model()

class MetadataValidationTestCase(TestCase):
    """Test case for metadata input validation."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.document = Document.objects.create(
            title='Test Document',
            description='Test document description',
            document_type='other',
            uploaded_by=self.user
        )
        self.metadata_field = CustomMetadataField.objects.create(
            name='Test Field',
            description='Test field description',
            field_type='text',
            created_by=self.user
        )
        self.metadata = DocumentMetadata.objects.create(
            document=self.document,
            field=self.metadata_field,
            value='Test value',
            created_by=self.user
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_metadata_field_missing_required_fields(self):
        """Test that creating a metadata field without required fields returns 400."""
        data = {
            # Missing required 'name' field
            'description': 'Test field description',
            'field_type': 'text'
        }
        # Update the URL to match the actual implementation
        response = self.client.post('/api/document-management/metadata-fields/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_metadata_field_invalid_type(self):
        """Test that creating a metadata field with invalid type returns 400."""
        data = {
            'name': 'Test Field',
            'description': 'Test field description',
            'field_type': 'invalid_type'  # Invalid field type
        }
        # Update the URL to match the actual implementation
        response = self.client.post('/api/document-management/metadata-fields/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_metadata_field_name_too_long(self):
        """Test that creating a metadata field with a name that's too long returns 400."""
        data = {
            'name': 'F' * 101,  # 101 characters, but max is 100
            'description': 'Test field description',
            'field_type': 'text'
        }
        # Update the URL to match the actual implementation
        response = self.client.post('/api/document-management/metadata-fields/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_metadata_field_invalid_options(self):
        """Test that creating a metadata field with invalid options returns 400."""
        data = {
            'name': 'Test Field',
            'description': 'Test field description',
            'field_type': 'select',
            'options': 'not-a-list'  # Should be a list
        }
        # Update the URL to match the actual implementation
        response = self.client.post('/api/document-management/metadata-fields/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_metadata_field_invalid_data(self):
        """Test that updating a metadata field with invalid data returns 400."""
        data = {
            'field_type': 'invalid_type'  # Invalid field type
        }
        # Update the URL to match the actual implementation
        response = self.client.patch(f'/api/document-management/metadata-fields/{self.metadata_field.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_document_metadata_missing_required_fields(self):
        """Test that creating document metadata without required fields returns 400."""
        data = {
            # Missing required 'field' field
            'document': self.document.id,
            'value': 'Test value'
        }
        response = self.client.post('/api/document-management/document-metadata/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('field', response.data)
    
    def test_create_document_metadata_invalid_field(self):
        """Test that creating document metadata with invalid field returns 400."""
        data = {
            'document': self.document.id,
            'field': 999,  # Non-existent field
            'value': 'Test value'
        }
        response = self.client.post('/api/document-management/document-metadata/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('field', response.data)
    
    def test_create_document_metadata_invalid_value_type(self):
        """Test that creating document metadata with invalid value type returns 400."""
        # Create a number field
        number_field = CustomMetadataField.objects.create(
            name='Number Field',
            description='Number field description',
            field_type='number',
            created_by=self.user
        )
        
        data = {
            'document': self.document.id,
            'field': number_field.id,
            'value': 'not-a-number'  # Invalid value for number field
        }
        response = self.client.post('/api/document-management/document-metadata/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('value', response.data)
    
    def test_create_document_metadata_invalid_select_value(self):
        """Test that creating document metadata with invalid select value returns 400."""
        # Create a select field with specific options
        select_field = CustomMetadataField.objects.create(
            name='Select Field',
            description='Select field description',
            field_type='select',
            options=['option1', 'option2', 'option3'],
            created_by=self.user
        )
        
        data = {
            'document': self.document.id,
            'field': select_field.id,
            'value': 'invalid_option'  # Not in the options list
        }
        response = self.client.post('/api/document-management/document-metadata/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('value', response.data)
    
    def test_update_document_metadata_invalid_data(self):
        """Test that updating document metadata with invalid data returns 400."""
        data = {
            'value': ''  # Empty value
        }
        response = self.client.patch(f'/api/document-management/document-metadata/{self.metadata.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('value', response.data)
    
    def test_bulk_update_metadata_invalid_data(self):
        """Test that bulk updating metadata with invalid data returns 400."""
        data = {
            'metadata': [
                {
                    'id': self.metadata.id,
                    'value': ''  # Empty value
                }
            ]
        }
        response = self.client.post(f'/api/document-management/documents/{self.document.id}/update-metadata/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('metadata', response.data)
