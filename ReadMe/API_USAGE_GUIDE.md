# API Usage Guide

This guide provides practical examples for using the CRM Loan Management System API.

## Authentication

Before using the API, you need to authenticate:

```
POST /api/auth/token/
{
  "username": "your_username",
  "password": "your_password"
}
```

Include the token in all subsequent requests:
```
Authorization: Token your_auth_token
```

Note: For testing purposes, authentication has been temporarily disabled on document management endpoints.

## Document Management Workflow

### 1. Create a Document

```
POST /api/document-management/documents/
```

Request (multipart/form-data):
```
title: Loan Agreement
description: Standard loan agreement for mortgage application
document_type: agreement
file: [FILE_UPLOAD]
```

Response:
```json
{
  "id": 1,
  "title": "Loan Agreement",
  "description": "Standard loan agreement for mortgage application",
  "document_type": "agreement",
  "file": "/media/documents/2025/04/11/agreement/loan_agreement.pdf",
  "status": "draft",
  "created_at": "2025-04-11T03:30:00Z",
  "updated_at": "2025-04-11T03:30:00Z"
}
```

### 2. Request Document Approval

```
POST /api/document-management/documents/1/request_approval/
```

Request:
```json
{
  "reviewers": [2, 3],
  "approval_level": 2,
  "comments": "Please review this loan agreement"
}
```

Response:
```json
{
  "id": 1,
  "document": 1,
  "reviewers": [
    {
      "id": 2,
      "username": "manager1"
    },
    {
      "id": 3,
      "username": "manager2"
    }
  ],
  "status": "pending",
  "requested_by": 1,
  "requested_date": "2025-04-11T03:35:00Z",
  "comments": "Please review this loan agreement"
}
```

## Document Organization

### 1. Create a Collection

```
POST /api/document-management/collections/
```

Request:
```json
{
  "name": "Loan Applications",
  "description": "All loan application documents",
  "parent": null,
  "icon": "fa-folder",
  "color": "#4287f5"
}
```

Response:
```json
{
  "id": 1,
  "name": "Loan Applications",
  "description": "All loan application documents",
  "created_by": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "first_name": "Admin",
    "last_name": "User"
  },
  "created_at": "2025-04-11T04:15:00Z",
  "updated_at": "2025-04-11T04:15:00Z",
  "is_shared": false,
  "shared_with": [],
  "parent": null,
  "parent_name": null,
  "full_path": "Loan Applications",
  "icon": "fa-folder",
  "color": "#4287f5",
  "document_count": 0
}
```

### 2. Create a Subcollection

```
POST /api/document-management/collections/
```

Request:
```json
{
  "name": "Mortgage Documents",
  "description": "Mortgage-related documents",
  "parent": 1,
  "icon": "fa-folder",
  "color": "#42f5a7"
}
```

### 3. Add Document to Collection

```
POST /api/document-management/documents/1/add_to_collection/
```

Request:
```json
{
  "collection_id": 1
}
```

Response:
```json
{
  "status": "Document added to collection"
}
```

### 4. Share a Collection

```
POST /api/document-management/collections/1/share/
```

Request:
```json
{
  "user_ids": [2, 3, 4]
}
```

Response:
```json
{
  "id": 1,
  "name": "Loan Applications",
  "description": "All loan application documents",
  "created_by": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "first_name": "Admin",
    "last_name": "User"
  },
  "created_at": "2025-04-11T04:15:00Z",
  "updated_at": "2025-04-11T04:15:00Z",
  "is_shared": true,
  "shared_with": [
    {
      "id": 2,
      "username": "manager1"
    },
    {
      "id": 3,
      "username": "manager2"
    },
    {
      "id": 4,
      "username": "user1"
    }
  ],
  "parent": null,
  "parent_name": null,
  "full_path": "Loan Applications",
  "icon": "fa-folder",
  "color": "#4287f5",
  "document_count": 1
}
```

## Document Relationships

### 1. Create a Relationship

```
POST /api/document-management/relationships/
```

Request:
```json
{
  "source_document": 1,
  "target_document": 2,
  "relationship_type": "supersedes",
  "description": "This agreement supersedes the previous version"
}
```

Response:
```json
{
  "id": 1,
  "source_document": 1,
  "source_document_title": "Loan Agreement",
  "target_document": 2,
  "target_document_title": "Loan Amendment",
  "relationship_type": "supersedes",
  "custom_type": null,
  "relationship_display": "Supersedes",
  "description": "This agreement supersedes the previous version",
  "created_by": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "first_name": "Admin",
    "last_name": "User"
  },
  "created_at": "2025-04-11T04:30:00Z"
}
```

### 2. Create a Custom Relationship

```
POST /api/document-management/relationships/
```

Request:
```json
{
  "source_document": 1,
  "target_document": 3,
  "relationship_type": "custom",
  "custom_type": "depends_on",
  "description": "This document depends on the referenced document"
}
```

### 3. Get Document Relationships

```
GET /api/document-management/documents/1/relationships/
```

Response:
```json
[
  {
    "id": 2,
    "title": "Loan Amendment",
    "document_type": "agreement",
    "relationship": "supersedes",
    "custom_type": null,
    "direction": "outgoing"
  },
  {
    "id": 3,
    "title": "Property Appraisal",
    "document_type": "property",
    "relationship": "custom",
    "custom_type": "depends_on",
    "direction": "outgoing"
  }
]
```

## Custom Metadata

### 1. Create a Metadata Field

```
POST /api/document-management/metadata-fields/
```

Request:
```json
{
  "name": "Property Address",
  "description": "Address of the property",
  "field_type": "text",
  "required": true,
  "document_types": ["property", "agreement"]
}
```

Response:
```json
{
  "id": 1,
  "name": "Property Address",
  "description": "Address of the property",
  "field_type": "text",
  "required": true,
  "default_value": null,
  "options": null,
  "document_types": ["property", "agreement"],
  "created_by": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "first_name": "Admin",
    "last_name": "User"
  },
  "created_at": "2025-04-11T04:40:00Z"
}
```

### 2. Create a Select Field

```
POST /api/document-management/metadata-fields/
```

Request:
```json
{
  "name": "Document Status",
  "description": "Custom status for document",
  "field_type": "select",
  "required": false,
  "default_value": "pending",
  "options": ["pending", "in_review", "final", "archived"]
}
```

### 3. Add Metadata to a Document

```
POST /api/document-management/documents/1/add_metadata/
```

Request:
```json
{
  "field_id": 1,
  "value": "123 Main St, Anytown, CA 12345"
}
```

Response:
```json
{
  "id": 1,
  "document": 1,
  "field": {
    "id": 1,
    "name": "Property Address",
    "description": "Address of the property",
    "field_type": "text",
    "required": true,
    "default_value": null,
    "options": null,
    "document_types": ["property", "agreement"],
    "created_by": {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "first_name": "Admin",
      "last_name": "User"
    },
    "created_at": "2025-04-11T04:40:00Z"
  },
  "value": "123 Main St, Anytown, CA 12345",
  "created_by": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "first_name": "Admin",
    "last_name": "User"
  },
  "created_at": "2025-04-11T04:45:00Z",
  "updated_at": "2025-04-11T04:45:00Z"
}
```

### 4. Get Metadata Fields for Document Type

```
GET /api/document-management/metadata-fields/for_document_type/?document_type=agreement
```

Response:
```json
[
  {
    "id": 1,
    "name": "Property Address",
    "description": "Address of the property",
    "field_type": "text",
    "required": true,
    "default_value": null,
    "options": null,
    "document_types": ["property", "agreement"],
    "created_by": {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "first_name": "Admin",
      "last_name": "User"
    },
    "created_at": "2025-04-11T04:40:00Z"
  }
]
```

## Document Organization Actions

### 1. Toggle Favorite Status

```
POST /api/document-management/documents/1/toggle_favorite/
```

Response:
```json
{
  "is_favorite": true
}
```

### 2. Toggle Pinned Status

```
POST /api/document-management/documents/1/toggle_pinned/
```

Response:
```json
{
  "is_pinned": true
}
```

## Document Search

### Basic Search

```
GET /api/document-management/search/?q=loan
```

Response:
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Loan Agreement",
      "description": "Standard loan agreement for mortgage application",
      "document_type": "agreement",
      "status": "approved",
      "created_at": "2025-04-11T03:30:00Z",
      "updated_at": "2025-04-11T03:30:00Z"
    }
  ],
  "query": "loan"
}
```

### Advanced Search with Filters

```
GET /api/document-management/search/?q=loan&document_type=agreement&status=approved&date_from=2025-04-01T00:00:00Z&date_to=2025-04-30T23:59:59Z&ordering=-created_at
```

## Common Workflows

### Complete Loan Application Process

1. Create a borrower
2. Create a loan application
3. Upload required documents
4. Request document approvals
5. Generate loan agreement
6. Request signatures on the loan agreement
7. Finalize the loan application

### Document Organization Workflow

1. Create document categories and collections
2. Upload documents and assign to categories/collections
3. Add custom metadata to documents
4. Establish relationships between related documents
5. Mark important documents as favorites or pinned
6. Share collections with team members

## Error Handling

All API endpoints follow a consistent error response format:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {
    "field_name": ["Error details"]
  }
}
```

## Troubleshooting

### Authentication Issues

If you receive 401 Unauthorized errors:
- Check that you're including the authentication token
- Verify that your token is valid and not expired
- For testing, use endpoints with temporarily disabled authentication

### Document Search Issues

If search results are not as expected:
- Ensure the search index is built: `python manage.py rebuild_document_index`
- Check that documents exist in the database
- Verify that document content is properly extracted (depends on textract)

### API Request Issues

When using URL parameters with IDs:
- Replace `{id}` placeholders with actual numeric IDs
- Example: Use `/api/document-management/documents/1/request_approval/` instead of `/api/document-management/documents/{id}/request_approval/`
