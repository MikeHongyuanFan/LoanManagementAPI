# API User Guide

This guide provides practical examples and usage instructions for the CRM Loan Management System API.

## Table of Contents

1. [Authentication](#authentication)
2. [Common Patterns](#common-patterns)
3. [Document Management](#document-management)
4. [Loan Applications](#loan-applications)
5. [Borrower Management](#borrower-management)
6. [Broker Management](#broker-management)
7. [Loan Calculator](#loan-calculator)
8. [Notifications](#notifications)
9. [Products](#products)
10. [Advanced Filtering and Searching](#advanced-filtering-and-searching)
11. [Error Handling](#error-handling)
12. [Best Practices](#best-practices)

## Authentication

Before using any API endpoint, you need to authenticate. The system uses JWT (JSON Web Token) authentication.

### Getting an Authentication Token

```
POST /api/auth/token/
```

Request:
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Using the Token

Include the token in the Authorization header for all subsequent requests:

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### Refreshing the Token

When the access token expires, use the refresh token to get a new one:

```
POST /api/auth/token/refresh/
```

Request:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## Common Patterns

Most resources follow RESTful conventions with standard CRUD operations:

- **GET** - Retrieve resources
- **POST** - Create resources
- **PUT** - Update resources (full update)
- **PATCH** - Update resources (partial update)
- **DELETE** - Delete resources

### Pagination

List endpoints return paginated results:

```json
{
  "count": 100,
  "next": "http://api.example.com/api/resource/?page=2",
  "previous": null,
  "results": [...]
}
```

Navigate pages using the `page` parameter:
```
GET /api/resource/?page=2
```

### Response Status Codes

- **200 OK** - Request succeeded
- **201 Created** - Resource created successfully
- **204 No Content** - Request succeeded with no response body (e.g., after DELETE)
- **400 Bad Request** - Invalid request data
- **401 Unauthorized** - Authentication required
- **403 Forbidden** - Permission denied
- **404 Not Found** - Resource not found
- **500 Internal Server Error** - Server error

## Document Management

### Working with Documents

#### List All Documents

```
GET /api/document-management/documents/
```

Response:
```json
{
  "count": 25,
  "next": "http://api.example.com/api/document-management/documents/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Loan Agreement",
      "description": "Standard loan agreement",
      "document_type": "agreement",
      "status": "active",
      "file": "http://api.example.com/media/documents/loan_agreement.pdf",
      "created_at": "2025-04-01T10:30:00Z",
      "updated_at": "2025-04-01T10:30:00Z"
    },
    // More documents...
  ]
}
```

#### Create a New Document

```
POST /api/document-management/documents/
```

Request (multipart/form-data):
```
title: Loan Agreement
description: Standard loan agreement
document_type: agreement
file: [binary file data]
category: 1
application: 5
```

Response:
```json
{
  "id": 26,
  "title": "Loan Agreement",
  "description": "Standard loan agreement",
  "document_type": "agreement",
  "status": "active",
  "file": "http://api.example.com/media/documents/loan_agreement.pdf",
  "created_at": "2025-04-11T10:30:00Z",
  "updated_at": "2025-04-11T10:30:00Z"
}
```

#### Get Document Details

```
GET /api/document-management/documents/26/
```

#### Update a Document

```
PATCH /api/document-management/documents/26/
```

Request:
```json
{
  "title": "Updated Loan Agreement",
  "status": "archived"
}
```

#### Delete a Document

```
DELETE /api/document-management/documents/26/
```

### Document Organization

#### Add Document to Collection

```
POST /api/document-management/documents/26/add_to_collection/
```

Request:
```json
{
  "collection_id": 5
}
```

#### Toggle Favorite Status

```
POST /api/document-management/documents/26/toggle_favorite/
```

Response:
```json
{
  "is_favorite": true
}
```

#### Add Custom Metadata

```
POST /api/document-management/documents/26/add_metadata/
```

Request:
```json
{
  "field_id": 3,
  "value": "123 Main St, Anytown, CA 12345"
}
```

### Document Relationships

#### Create a Relationship Between Documents

```
POST /api/document-management/relationships/
```

Request:
```json
{
  "source_document": 26,
  "target_document": 15,
  "relationship_type": "supersedes",
  "description": "This is the updated version of the agreement"
}
```

#### Get All Relationships for a Document

```
GET /api/document-management/documents/26/relationships/
```

### Document Approval Workflow

#### Create an Approval Request

```
POST /api/document-management/approvals/
```

Request:
```json
{
  "document": 26,
  "reviewer": 5,
  "due_date": "2025-04-20T00:00:00Z",
  "comments": "Please review this updated loan agreement"
}
```

#### Approve a Document

```
POST /api/document-management/approvals/10/approve/
```

Request:
```json
{
  "comments": "Approved. All terms look good."
}
```

#### Reject a Document

```
POST /api/document-management/approvals/10/reject/
```

Request:
```json
{
  "comments": "Rejected. Please fix the interest rate section."
}
```

### Electronic Signatures

#### Create a Signature Request

```
POST /api/document-management/signature-requests/
```

Request:
```json
{
  "document": 26,
  "signer": 8,
  "due_date": "2025-04-25T00:00:00Z",
  "message": "Please sign this loan agreement"
}
```

#### Sign a Document

```
POST /api/document-management/signature-requests/5/sign/
```

Request:
```json
{
  "signature_data": "base64_encoded_signature_data",
  "comments": "Signed and accepted"
}
```

#### Decline to Sign

```
POST /api/document-management/signature-requests/5/decline/
```

Request:
```json
{
  "reason": "Terms are not acceptable"
}
```

## Loan Applications

### Managing Applications

#### List All Applications

```
GET /api/applications/
```

#### Create a New Application

```
POST /api/applications/
```

Request:
```json
{
  "borrower": 12,
  "broker": 5,
  "product": 3,
  "loan_amount": 250000,
  "loan_term": 24,
  "interest_rate": 5.75,
  "purpose": "Property development",
  "property_address": "456 Development Ave, Cityville, CA 54321"
}
```

#### Transition Application Status

```
POST /api/applications/8/transition/
```

Request:
```json
{
  "status": "approved",
  "comments": "Application meets all criteria"
}
```

#### Duplicate an Application

```
POST /api/applications/8/duplicate/
```

Response:
```json
{
  "id": 15,
  "borrower": 12,
  "broker": 5,
  "product": 3,
  "loan_amount": 250000,
  "loan_term": 24,
  "interest_rate": 5.75,
  "purpose": "Property development",
  "property_address": "456 Development Ave, Cityville, CA 54321",
  "status": "draft",
  "created_at": "2025-04-11T11:45:00Z"
}
```

### Supporting Entities

#### Create a Valuer

```
POST /api/valuers/
```

Request:
```json
{
  "name": "ABC Valuation Services",
  "contact_name": "John Smith",
  "email": "john@abcvaluation.com",
  "phone": "555-123-4567",
  "address": "789 Valuation St, Cityville, CA 54321"
}
```

#### Create a Fee

```
POST /api/fees/
```

Request:
```json
{
  "application": 8,
  "fee_type": "valuation",
  "amount": 750.00,
  "description": "Property valuation fee",
  "due_date": "2025-04-20T00:00:00Z"
}
```

## Borrower Management

#### List All Borrowers

```
GET /api/borrowers/
```

#### Create a New Borrower

```
POST /api/borrowers/
```

Request:
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane.smith@example.com",
  "phone_number": "555-987-6543",
  "address": "123 Main St, Anytown, CA 12345",
  "date_of_birth": "1985-06-15",
  "employment_status": "employed",
  "annual_income": 85000
}
```

#### Update a Borrower

```
PATCH /api/borrowers/12/
```

Request:
```json
{
  "phone_number": "555-111-2222",
  "address": "456 New St, Anytown, CA 12345"
}
```

## Broker Management

#### List All Brokers

```
GET /api/brokers/
```

#### Create a New Broker

```
POST /api/brokers/
```

Request:
```json
{
  "first_name": "Michael",
  "last_name": "Johnson",
  "email": "michael.johnson@example.com",
  "phone_number": "555-444-3333",
  "company_name": "Johnson Financial Services",
  "license_number": "BRK12345",
  "address": "789 Broker Ave, Cityville, CA 54321"
}
```

## Loan Calculator

#### Calculate Loan Details

```
POST /api/calculator/calculations/calculate/
```

Request:
```json
{
  "loan_amount": 250000,
  "loan_term": 24,
  "interest_rate": 5.75,
  "payment_frequency": "monthly",
  "interest_only_period": 0,
  "fees": [
    {
      "fee_type": "establishment",
      "amount": 1500
    },
    {
      "fee_type": "valuation",
      "amount": 750
    }
  ]
}
```

Response:
```json
{
  "monthly_payment": 11042.15,
  "total_repayment": 264811.60,
  "total_interest": 14811.60,
  "total_fees": 2250.00,
  "total_cost": 267061.60,
  "repayment_schedule": [
    {
      "period": 1,
      "payment_date": "2025-05-11",
      "payment_amount": 11042.15,
      "principal": 9843.40,
      "interest": 1198.75,
      "balance": 240156.60
    },
    // More periods...
  ]
}
```

#### Waive a Fee

```
POST /api/calculator/application-fees/5/waive/
```

Request:
```json
{
  "reason": "Promotional offer",
  "waived_by": 1
}
```

## Notifications

#### Get Unread Notifications

```
GET /api/notifications/unread/
```

#### Create a Note

```
POST /api/notes/
```

Request:
```json
{
  "application": 8,
  "content": "Called borrower to discuss additional documentation requirements",
  "reminder_date": "2025-04-15T00:00:00Z"
}
```

## Products

#### List All Products

```
GET /api/products/
```

#### Create a New Product

```
POST /api/products/
```

Request:
```json
{
  "name": "Commercial Development Loan",
  "description": "Short-term loan for commercial property development",
  "min_loan_amount": 100000,
  "max_loan_amount": 5000000,
  "min_term": 12,
  "max_term": 36,
  "base_interest_rate": 5.5,
  "is_active": true
}
```

## Advanced Filtering and Searching

### Filtering

Most list endpoints support filtering using query parameters:

```
GET /api/document-management/documents/?document_type=agreement&status=active
```

### Searching

Search functionality is available on many endpoints:

```
GET /api/borrowers/?search=smith
```

### Ordering

Control the order of results:

```
GET /api/applications/?ordering=-created_at
```

Use a minus sign (`-`) to indicate descending order.

### Combined Example

```
GET /api/document-management/documents/?document_type=agreement&status=active&search=loan&ordering=-created_at&page=2
```

## Error Handling

### Common Error Responses

#### Validation Error (400 Bad Request)

```json
{
  "field_name": [
    "Error message about this field"
  ],
  "another_field": [
    "Another error message"
  ]
}
```

#### Authentication Error (401 Unauthorized)

```json
{
  "detail": "Authentication credentials were not provided."
}
```

#### Permission Error (403 Forbidden)

```json
{
  "detail": "You do not have permission to perform this action."
}
```

#### Not Found Error (404 Not Found)

```json
{
  "detail": "Not found."
}
```

## Best Practices

1. **Always authenticate** before making API requests
2. **Use HTTPS** for all API calls to ensure security
3. **Handle pagination** properly for list endpoints
4. **Validate input data** before sending to the API
5. **Implement proper error handling** in your client application
6. **Use filtering and searching** to minimize data transfer
7. **Cache responses** when appropriate to improve performance
8. **Refresh tokens** before they expire to maintain session
9. **Use partial updates** (PATCH) when only updating a few fields
10. **Follow rate limits** to avoid being throttled

## API Versioning

The current API version is v1. The version is included in the URL path:

```
/api/v1/resource/
```

When a new version is released, both versions will be supported for a transition period.
