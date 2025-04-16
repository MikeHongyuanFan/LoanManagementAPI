# Document Management API Service

## Overview

The Document Management API service handles all document-related operations within the Loan Management System. It provides comprehensive functionality for document creation, storage, organization, versioning, approval workflows, and electronic signatures.

## Service Functions

### Primary Functions

1. **Document Management**
   - Create, retrieve, update, and delete documents
   - Organize documents into categories and collections
   - Manage document metadata and relationships
   - Support document versioning

2. **Approval Workflows**
   - Request document approvals
   - Process approval responses
   - Track approval status
   - Manage multi-step approval processes

3. **Electronic Signatures**
   - Request document signatures
   - Process signature responses
   - Verify signature authenticity
   - Store signature data securely

4. **Document Organization**
   - Categorize documents
   - Create document collections
   - Establish relationships between documents
   - Add custom metadata to documents

## Data Flow

### Input Data

- **Document Files**: PDF, DOCX, JPG, PNG files
- **Document Metadata**: Title, description, type, category
- **Workflow Requests**: Approval and signature requests
- **Organization Data**: Categories, collections, relationships

### Output Data

- **Document Information**: Document details with metadata
- **Workflow Status**: Approval and signature status
- **Organization Structure**: Category hierarchies and collections
- **Relationship Maps**: Document relationship networks

### Internal Processing

1. **Validation Layer**:
   - Validates document files and metadata
   - Ensures proper file types and sizes
   - Validates workflow requests

2. **Business Logic Layer**:
   - Processes document uploads and updates
   - Manages approval and signature workflows
   - Handles document organization and relationships

3. **Data Access Layer**:
   - Interacts with the database models
   - Manages file storage
   - Handles query optimization

## Integration Communication

### Inbound Integrations

1. **User Interface**:
   - Receives document upload and management requests
   - Handles workflow action requests

2. **Authentication Service**:
   - Receives user authentication and authorization information
   - Validates user permissions for document actions

3. **Applications API**:
   - Receives requests to associate documents with applications
   - Provides application context for documents

### Outbound Integrations

1. **Notifications API**:
   - Sends notification triggers for document events
   - Receives notification delivery confirmations

2. **Storage Service**:
   - Sends document files for storage
   - Retrieves document files when requested

3. **Search Service**:
   - Sends document content for indexing
   - Receives search results

## API Reference

### Endpoints

#### Document Management

```
GET /api/document-management/documents/
```
- **Description**: List all documents with optional filtering
- **Query Parameters**:
  - `application`: Filter by application ID
  - `category`: Filter by category ID
  - `document_type`: Filter by document type
  - `status`: Filter by document status
  - `search`: Search by title or description
- **Response**: List of document objects with pagination

```
POST /api/document-management/documents/
```
- **Description**: Create a new document
- **Request Body**:
  - `title`: Document title (required)
  - `description`: Document description (optional)
  - `file`: Document file (required)
  - `document_type`: Document type (required)
  - `application_id`: Associated application ID (optional)
  - `category_id`: Category ID (optional)
  - `tags`: Array of tag names (optional)
  - `keywords`: Comma-separated keywords (optional)
  - `access_level`: Access level (1-5, default: 1)
  - `is_confidential`: Whether the document is confidential (default: false)
- **Response**: Created document object

```
GET /api/document-management/documents/{id}/
```
- **Description**: Retrieve a specific document
- **Path Parameters**:
  - `id`: Document ID
- **Response**: Document object with related entities

```
PUT /api/document-management/documents/{id}/
```
- **Description**: Update a document
- **Path Parameters**:
  - `id`: Document ID
- **Request Body**: Document fields to update
- **Response**: Updated document object

```
DELETE /api/document-management/documents/{id}/
```
- **Description**: Delete a document
- **Path Parameters**:
  - `id`: Document ID
- **Response**: Success message

#### Document Categories

```
GET /api/document-management/categories/
```
- **Description**: List all document categories
- **Query Parameters**:
  - `parent`: Filter by parent category ID
- **Response**: List of category objects

```
POST /api/document-management/categories/
```
- **Description**: Create a new document category
- **Request Body**:
  - `name`: Category name (required)
  - `description`: Category description (optional)
  - `parent_id`: Parent category ID (optional)
  - `icon`: Icon class name (optional)
  - `color`: Color code (optional)
- **Response**: Created category object

```
GET /api/document-management/categories/{id}/
```
- **Description**: Retrieve a specific category
- **Path Parameters**:
  - `id`: Category ID
- **Response**: Category object

#### Document Collections

```
GET /api/document-management/collections/
```
- **Description**: List all document collections
- **Query Parameters**:
  - `created_by`: Filter by creator user ID
  - `is_shared`: Filter by shared status
- **Response**: List of collection objects

```
POST /api/document-management/collections/
```
- **Description**: Create a new document collection
- **Request Body**:
  - `name`: Collection name (required)
  - `description`: Collection description (optional)
  - `is_shared`: Whether the collection is shared (default: false)
  - `shared_with`: Array of user IDs to share with (optional)
  - `parent_id`: Parent collection ID (optional)
  - `icon`: Icon class name (optional)
  - `color`: Color code (optional)
- **Response**: Created collection object

```
GET /api/document-management/collections/{id}/
```
- **Description**: Retrieve a specific collection
- **Path Parameters**:
  - `id`: Collection ID
- **Response**: Collection object with documents

```
POST /api/document-management/collections/{id}/add-documents/
```
- **Description**: Add documents to a collection
- **Path Parameters**:
  - `id`: Collection ID
- **Request Body**:
  - `document_ids`: Array of document IDs to add
- **Response**: Updated collection object

```
POST /api/document-management/collections/{id}/remove-documents/
```
- **Description**: Remove documents from a collection
- **Path Parameters**:
  - `id`: Collection ID
- **Request Body**:
  - `document_ids`: Array of document IDs to remove
- **Response**: Updated collection object

#### Document Relationships

```
GET /api/document-management/relationships/
```
- **Description**: List all document relationships
- **Query Parameters**:
  - `source_document`: Filter by source document ID
  - `target_document`: Filter by target document ID
  - `relationship_type`: Filter by relationship type
- **Response**: List of relationship objects

```
POST /api/document-management/relationships/add/
```
- **Description**: Create a new document relationship
- **Request Body**:
  - `source_document_id`: Source document ID (required)
  - `target_document_id`: Target document ID (required)
  - `relationship_type`: Relationship type (required)
  - `custom_type`: Custom relationship type name (required if relationship_type is 'custom')
  - `description`: Relationship description (optional)
- **Response**: Created relationship object

```
GET /api/document-management/documents/{id}/relationships/
```
- **Description**: Get all relationships for a document
- **Path Parameters**:
  - `id`: Document ID
- **Response**: List of relationship objects

```
POST /api/document-management/documents/{id}/add-relationship/
```
- **Description**: Add a relationship to a document
- **Path Parameters**:
  - `id`: Source document ID
- **Request Body**:
  - `target_document_id`: Target document ID (required)
  - `relationship_type`: Relationship type (required)
  - `custom_type`: Custom relationship type name (required if relationship_type is 'custom')
  - `description`: Relationship description (optional)
- **Response**: Created relationship object

#### Document Approval Workflows

```
GET /api/document-management/approvals/
```
- **Description**: List all document approvals
- **Query Parameters**:
  - `document`: Filter by document ID
  - `reviewer`: Filter by reviewer user ID
  - `status`: Filter by approval status
- **Response**: List of approval objects

```
POST /api/document-management/documents/{id}/request-approval/
```
- **Description**: Request approval for a document
- **Path Parameters**:
  - `id`: Document ID
- **Request Body**:
  - `reviewer_id`: Reviewer user ID (required)
  - `comments`: Request comments (optional)
  - `approval_level`: Approval level (1-5, default: 1)
- **Response**: Created approval request object

```
POST /api/document-management/approvals/{id}/respond/
```
- **Description**: Respond to an approval request
- **Path Parameters**:
  - `id`: Approval request ID
- **Request Body**:
  - `status`: Response status ('approved' or 'rejected', required)
  - `comments`: Response comments (optional)
- **Response**: Updated approval object

#### Document Signature Workflows

```
GET /api/document-management/signature-requests/
```
- **Description**: List all signature requests
- **Query Parameters**:
  - `document`: Filter by document ID
  - `signer`: Filter by signer user ID
  - `status`: Filter by signature request status
- **Response**: List of signature request objects

```
POST /api/document-management/documents/{id}/request-signature/
```
- **Description**: Request signature for a document
- **Path Parameters**:
  - `id`: Document ID
- **Request Body**:
  - `signer_id`: Signer user ID (required)
  - `message`: Request message (optional)
  - `due_date`: Due date for signature (optional)
- **Response**: Created signature request object

```
POST /api/document-management/signature-requests/{id}/respond/
```
- **Description**: Respond to a signature request
- **Path Parameters**:
  - `id`: Signature request ID
- **Request Body**:
  - `action`: Response action ('sign' or 'decline', required)
  - `signature_type`: Signature type ('drawn', 'typed', or 'digital', required if action is 'sign')
  - `signature_data`: Signature data (required if action is 'sign')
  - `decline_reason`: Reason for declining (required if action is 'decline')
- **Response**: Updated signature request object with signature if signed

#### Document Comments

```
GET /api/document-management/documents/{id}/comments/
```
- **Description**: Get all comments for a document
- **Path Parameters**:
  - `id`: Document ID
- **Response**: List of comment objects

```
POST /api/document-management/documents/{id}/comments/create/
```
- **Description**: Add a comment to a document
- **Path Parameters**:
  - `id`: Document ID
- **Request Body**:
  - `text`: Comment text (required)
- **Response**: Created comment object

```
PUT /api/document-management/comments/{id}/
```
- **Description**: Update a comment
- **Path Parameters**:
  - `id`: Comment ID
- **Request Body**:
  - `text`: Updated comment text (required)
- **Response**: Updated comment object

```
DELETE /api/document-management/comments/{id}/
```
- **Description**: Delete a comment
- **Path Parameters**:
  - `id`: Comment ID
- **Response**: Success message

### Data Models

#### Document Model

```json
{
  "id": 1,
  "title": "Loan Agreement",
  "description": "Official loan agreement document",
  "file": "/media/documents/2023/06/15/agreement/loan_agreement.pdf",
  "document_type": "agreement",
  "application": {
    "id": 1,
    "borrower": "John Doe",
    "status": "under_review"
  },
  "category": {
    "id": 3,
    "name": "Agreements",
    "parent": null
  },
  "collections": [
    {
      "id": 2,
      "name": "Loan Documents"
    }
  ],
  "tags": ["agreement", "official"],
  "keywords": "loan, agreement, official",
  "status": "approved",
  "access_level": 3,
  "is_confidential": true,
  "is_favorite": false,
  "is_pinned": true,
  "expiration_date": null,
  "uploaded_by": {
    "id": 5,
    "username": "loan_officer"
  },
  "last_modified_by": {
    "id": 5,
    "username": "loan_officer"
  },
  "created_at": "2023-06-15T10:30:00Z",
  "updated_at": "2023-06-16T14:45:00Z",
  "version": 1,
  "version_notes": "Initial version",
  "is_latest_version": true,
  "related_documents": [
    {
      "document": {
        "id": 2,
        "title": "Loan Application Form"
      },
      "relationship": "references",
      "direction": "outgoing"
    }
  ],
  "approvals": [
    {
      "id": 1,
      "reviewer": "manager1",
      "status": "approved",
      "requested_date": "2023-06-15T11:30:00Z",
      "response_date": "2023-06-15T14:20:00Z"
    }
  ],
  "signature_requests": [
    {
      "id": 1,
      "signer": "john.doe",
      "status": "signed",
      "requested_date": "2023-06-15T15:00:00Z",
      "response_date": "2023-06-15T16:45:00Z"
    }
  ],
  "comments": [
    {
      "id": 1,
      "user": "loan_officer",
      "text": "Final version ready for signature",
      "created_at": "2023-06-15T10:35:00Z"
    }
  ]
}
```

## Error Handling

The Document Management API uses standard HTTP status codes and provides detailed error messages:

- **400 Bad Request**: Invalid input data
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **409 Conflict**: Business rule violation (e.g., invalid workflow transition)
- **413 Payload Too Large**: File size exceeds limit
- **415 Unsupported Media Type**: Unsupported file type
- **500 Internal Server Error**: Server-side error

Error responses include:
- Error code
- Error message
- Detailed description (when applicable)
- Field-specific errors (for validation errors)

## Security

- **Authentication**: JWT-based authentication required for all endpoints
- **Authorization**: Role-based access control for different operations
- **Access Levels**: Document access levels control visibility
- **Data Validation**: Input validation to prevent injection attacks
- **File Validation**: File type and content validation
- **Audit Logging**: All document actions are logged with user information

## Performance Considerations

- **Database Optimization**: Indexes on frequently queried fields (status, document_type, application_id)
- **Query Optimization**: Use of select_related and prefetch_related for related entities
- **Pagination**: All list endpoints support pagination to handle large datasets
- **File Storage**: Efficient file storage with proper directory structure
- **Caching**: Caching of document metadata and frequently accessed documents

## Implementation Notes

- The Document Management API is implemented using Django and Django REST Framework
- File storage uses Django's FileField with custom upload paths
- Document versioning is implemented with parent-child relationships
- Approval and signature workflows use state machines for status transitions
- Full-text search is implemented using Django Haystack with Whoosh
