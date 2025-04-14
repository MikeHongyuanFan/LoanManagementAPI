# Complete API Reference

This document contains every single API endpoint available in the CRM Loan Management System, extracted directly from the codebase.

## Document Management APIs

### Documents

| Exact API Path | HTTP Method | Description |
|----------------|-------------|-------------|
| `/api/document-management/documents/` | GET | List all documents |
| `/api/document-management/documents/` | POST | Create a new document |
| `/api/document-management/documents/{id}/` | GET | Get document details |
| `/api/document-management/documents/{id}/` | PUT | Update a document |
| `/api/document-management/documents/{id}/` | PATCH | Partially update a document |
| `/api/document-management/documents/{id}/` | DELETE | Delete a document |
| `/api/document-management/documents/{id}/add_to_collection/` | POST | Add document to collection |
| `/api/document-management/documents/{id}/remove_from_collection/` | POST | Remove document from collection |
| `/api/document-management/documents/{id}/toggle_favorite/` | POST | Toggle favorite status |
| `/api/document-management/documents/{id}/toggle_pinned/` | POST | Toggle pinned status |
| `/api/document-management/documents/{id}/add_metadata/` | POST | Add custom metadata to a document |
| `/api/document-management/documents/{id}/add_relationship/` | POST | Add a relationship to another document |
| `/api/document-management/documents/{id}/relationships/` | GET | Get all relationships for a document |
| `/api/document-management/documents/{id}/create-version/` | POST | Create a new version of a document |
| `/api/document-management/documents/{id}/versions/` | GET | Get all versions of a document |
| `/api/document-management/documents/{id}/revert/{version_id}/` | POST | Revert to a previous version |
| `/api/document-management/documents/{id}/request-approval/` | POST | Request approval for a document |
| `/api/document-management/documents/{id}/update-metadata/` | POST | Bulk update document metadata |

### Document Categories

| Exact API Path | HTTP Method | Description |
|----------------|-------------|-------------|
| `/api/document-management/categories/` | GET | List all categories |
| `/api/document-management/categories/` | POST | Create a new category |
| `/api/document-management/categories/{id}/` | GET | Get category details |
| `/api/document-management/categories/{id}/` | PUT | Update a category |
| `/api/document-management/categories/{id}/` | PATCH | Partially update a category |
| `/api/document-management/categories/{id}/` | DELETE | Delete a category |
| `/api/document-management/categories/{id}/subcategories/` | GET | Get all subcategories of a category |

### Document Templates

| Exact API Path | HTTP Method | Description |
|----------------|-------------|-------------|
| `/api/document-management/templates/` | GET | List all templates |
| `/api/document-management/templates/` | POST | Create a new template |
| `/api/document-management/templates/{id}/` | GET | Get template details |
| `/api/document-management/templates/{id}/` | PUT | Update a template |
| `/api/document-management/templates/{id}/` | PATCH | Partially update a template |
| `/api/document-management/templates/{id}/` | DELETE | Delete a template |

### Document Collections

| Exact API Path | HTTP Method | Description |
|----------------|-------------|-------------|
| `/api/document-management/collections/` | GET | List all collections |
| `/api/document-management/collections/` | POST | Create a new collection |
| `/api/document-management/collections/{id}/` | GET | Get collection details |
| `/api/document-management/collections/{id}/` | PUT | Update a collection |
| `/api/document-management/collections/{id}/` | PATCH | Partially update a collection |
| `/api/document-management/collections/{id}/` | DELETE | Delete a collection |
| `/api/document-management/collections/{id}/subcollections/` | GET | Get all subcollections of a collection |
| `/api/document-management/collections/{id}/documents/` | GET | Get all documents in a collection |
| `/api/document-management/collections/{id}/share/` | POST | Share a collection with users |
| `/api/document-management/collections/{id}/unshare/` | POST | Unshare a collection with users |

### Document Relationships

| Exact API Path | HTTP Method | Description |
|----------------|-------------|-------------|
| `/api/document-management/relationships/` | GET | List all relationships |
| `/api/document-management/relationships/` | POST | Create a new relationship |
| `/api/document-management/relationships/{id}/` | GET | Get relationship details |
| `/api/document-management/relationships/{id}/` | PUT | Update a relationship |
| `/api/document-management/relationships/{id}/` | PATCH | Partially update a relationship |
| `/api/document-management/relationships/{id}/` | DELETE | Delete a relationship |

### Custom Metadata

| Exact API Path | HTTP Method | Description |
|----------------|-------------|-------------|
| `/api/document-management/metadata-fields/` | GET | List all metadata fields |
| `/api/document-management/metadata-fields/` | POST | Create a new metadata field |
| `/api/document-management/metadata-fields/{id}/` | GET | Get metadata field details |
| `/api/document-management/metadata-fields/{id}/` | PUT | Update a metadata field |
| `/api/document-management/metadata-fields/{id}/` | PATCH | Partially update a metadata field |
| `/api/document-management/metadata-fields/{id}/` | DELETE | Delete a metadata field |
| `/api/document-management/metadata-fields/for_document_type/` | GET | Get metadata fields for a specific document type |
| `/api/document-management/metadata/` | GET | List all metadata values |
| `/api/document-management/metadata/` | POST | Create a new metadata value |
| `/api/document-management/metadata/{id}/` | GET | Get metadata value details |
| `/api/document-management/metadata/{id}/` | PUT | Update a metadata value |
| `/api/document-management/metadata/{id}/` | PATCH | Partially update a metadata value |
| `/api/document-management/metadata/{id}/` | DELETE | Delete a metadata value |

### Document Comments

| Exact API Path | HTTP Method | Description |
|----------------|-------------|-------------|
| `/api/document-management/comments/` | GET | List all comments |
| `/api/document-management/comments/` | POST | Create a new comment |
| `/api/document-management/comments/{id}/` | GET | Get comment details |
| `/api/document-management/comments/{id}/` | PUT | Update a comment |
| `/api/document-management/comments/{id}/` | PATCH | Partially update a comment |
| `/api/document-management/comments/{id}/` | DELETE | Delete a comment |

### Document Approval Workflow

| Exact API Path | HTTP Method | Description |
|----------------|-------------|-------------|
| `/api/document-management/approvals/` | GET | List all approvals |
| `/api/document-management/approvals/` | POST | Create a new approval |
| `/api/document-management/approvals/{id}/` | GET | Get approval details |
| `/api/document-management/approvals/{id}/` | PUT | Update an approval |
| `/api/document-management/approvals/{id}/` | PATCH | Partially update an approval |
| `/api/document-management/approvals/{id}/` | DELETE | Delete an approval |
| `/api/document-management/approvals/{id}/approve/` | POST | Approve a document |
| `/api/document-management/approvals/{id}/reject/` | POST | Reject a document |
| `/api/document-management/approvals/{id}/reassign/` | POST | Reassign approval to another reviewer |
| `/api/document-management/approvals/{id}/respond/` | POST | Respond to an approval request |
| `/api/document-management/approvals/{id}/cancel/` | POST | Cancel an approval request |

### Electronic Signature System

| Exact API Path | HTTP Method | Description |
|----------------|-------------|-------------|
| `/api/document-management/signature-requests/` | GET | List all signature requests |
| `/api/document-management/signature-requests/` | POST | Create a new signature request |
| `/api/document-management/signature-requests/{id}/` | GET | Get signature request details |
| `/api/document-management/signature-requests/{id}/` | PUT | Update a signature request |
| `/api/document-management/signature-requests/{id}/` | PATCH | Partially update a signature request |
| `/api/document-management/signature-requests/{id}/` | DELETE | Delete a signature request |
| `/api/document-management/signature-requests/{id}/sign/` | POST | Sign a document |
| `/api/document-management/signature-requests/{id}/decline/` | POST | Decline to sign a document |
| `/api/document-management/signature-requests/{id}/cancel/` | POST | Cancel a signature request |
| `/api/document-management/signature-requests/{id}/mark_as_viewed/` | POST | Mark a signature request as viewed |
| `/api/document-management/signature-requests/{id}/respond/` | POST | Respond to a signature request |
| `/api/document-management/signatures/` | GET | List all signatures |
| `/api/document-management/signatures/{id}/` | GET | Get signature details |
| `/api/document-management/signatures/{id}/verify/` | GET | Verify a signature |

### Document Search and Version Management

| Exact API Path | HTTP Method | Description |
|----------------|-------------|-------------|
| `/api/document-management/search/` | GET | Advanced document search with multiple filters |
| `/api/document-management/search/full-text/` | GET | Full-text search within document content |
| `/api/document-management/documents/recent/` | GET | Get recent documents for the current user |
| `/api/document-management/documents/suggestions/` | GET | Get document suggestions based on user activity |
| `/api/document-management/versions/compare/{version1_id}/{version2_id}/` | GET | Compare two document versions |

## Loan Application APIs

### Applications

| Exact API Path | HTTP Method | Description |
|----------------|-------------|-------------|
| `/api/applications/` | GET | List all applications |
| `/api/applications/` | POST | Create a new application |
| `/api/applications/{id}/` | GET | Get application details |
| `/api/applications/{id}/` | PUT | Update an application |
| `/api/applications/{id}/` | PATCH | Partially update an application |
| `/api/applications/{id}/` | DELETE | Delete an application |
| `/api/applications/{id}/transition/` | POST | Transition an application to a new stage or status |
| `/api/applications/{id}/duplicate/` | POST | Duplicate an application |

### Valuers

| Exact API Path | HTTP Method | Description |
|----------------|-------------|-------------|
| `/api/valuers/` | GET | List all valuers |
| `/api/valuers/` | POST | Create a new valuer |
| `/api/valuers/{id}/` | GET | Get valuer details |
| `/api/valuers/{id}/` | PUT | Update a valuer |
| `/api/valuers/{id}/` | PATCH | Partially update a valuer |
| `/api/valuers/{id}/` | DELETE | Delete a valuer |

### Quantity Surveyors (QS)

| Exact API Path | HTTP Method | Description |
|----------------|-------------|-------------|
| `/api/qs/` | GET | List all quantity surveyors |
| `/api/qs/` | POST | Create a new quantity surveyor |
| `/api/qs/{id}/` | GET | Get quantity surveyor details |
| `/api/qs/{id}/` | PUT | Update a quantity surveyor |
| `/api/qs/{id}/` | PATCH | Partially update a quantity surveyor |
| `/api/qs/{id}/` | DELETE | Delete a quantity surveyor |

### Referrals

| Exact API Path | HTTP Method | Description |
|----------------|-------------|-------------|
| `/api/referrals/` | GET | List all referrals |
| `/api/referrals/` | POST | Create a new referral |
| `/api/referrals/{id}/` | GET | Get referral details |
| `/api/referrals/{id}/` | PUT | Update a referral |
| `/api/referrals/{id}/` | PATCH | Partially update a referral |
| `/api/referrals/{id}/` | DELETE | Delete a referral |

### Fees

| Exact API Path | HTTP Method | Description |
|----------------|-------------|-------------|
| `/api/fees/` | GET | List all fees |
| `/api/fees/` | POST | Create a new fee |
| `/api/fees/{id}/` | GET | Get fee details |
| `/api/fees/{id}/` | PUT | Update a fee |
| `/api/fees/{id}/` | PATCH | Partially update a fee |
| `/api/fees/{id}/` | DELETE | Delete a fee |

### Repayments

| Exact API Path | HTTP Method | Description |
|----------------|-------------|-------------|
| `/api/repayments/` | GET | List all repayments |
| `/api/repayments/` | POST | Create a new repayment |
| `/api/repayments/{id}/` | GET | Get repayment details |
| `/api/repayments/{id}/` | PUT | Update a repayment |
| `/api/repayments/{id}/` | PATCH | Partially update a repayment |
| `/api/repayments/{id}/` | DELETE | Delete a repayment |

### Loan Extensions

| Exact API Path | HTTP Method | Description |
|----------------|-------------|-------------|
| `/api/loan-extensions/` | GET | List all loan extensions |
| `/api/loan-extensions/` | POST | Create a new loan extension |
| `/api/loan-extensions/{id}/` | GET | Get loan extension details |
| `/api/loan-extensions/{id}/` | PUT | Update a loan extension |
| `/api/loan-extensions/{id}/` | PATCH | Partially update a loan extension |
| `/api/loan-extensions/{id}/` | DELETE | Delete a loan extension |

## Borrower APIs

| Exact API Path | HTTP Method | Description |
|----------------|-------------|-------------|
| `/api/borrowers/` | GET | List all borrowers |
| `/api/borrowers/` | POST | Create a new borrower |
| `/api/borrowers/{id}/` | GET | Get borrower details |
| `/api/borrowers/{id}/` | PUT | Update a borrower |
| `/api/borrowers/{id}/` | PATCH | Partially update a borrower |
| `/api/borrowers/{id}/` | DELETE | Delete a borrower |

## Broker APIs

| Exact API Path | HTTP Method | Description |
|----------------|-------------|-------------|
| `/api/brokers/` | GET | List all brokers |
| `/api/brokers/` | POST | Create a new broker |
| `/api/brokers/{id}/` | GET | Get broker details |
| `/api/brokers/{id}/` | PUT | Update a broker |
| `/api/brokers/{id}/` | PATCH | Partially update a broker |
| `/api/brokers/{id}/` | DELETE | Delete a broker |

## Calculator APIs

| Exact API Path | HTTP Method | Description |
|----------------|-------------|-------------|
| `/api/calculator/calculations/` | GET | List all loan calculations |
| `/api/calculator/calculations/` | POST | Create a new loan calculation |
| `/api/calculator/calculations/{id}/` | GET | Get loan calculation details |
| `/api/calculator/calculations/{id}/` | PUT | Update a loan calculation |
| `/api/calculator/calculations/{id}/` | PATCH | Partially update a loan calculation |
| `/api/calculator/calculations/{id}/` | DELETE | Delete a loan calculation |
| `/api/calculator/calculations/calculate/` | POST | Calculate loan details based on input parameters |
| `/api/calculator/repayments/` | GET | List all repayment schedules |
| `/api/calculator/repayments/{id}/` | GET | Get repayment schedule details |
| `/api/calculator/fees/` | GET | List all calculator fees |
| `/api/calculator/fees/` | POST | Create a new calculator fee |
| `/api/calculator/fees/{id}/` | GET | Get calculator fee details |
| `/api/calculator/fees/{id}/` | PUT | Update a calculator fee |
| `/api/calculator/fees/{id}/` | PATCH | Partially update a calculator fee |
| `/api/calculator/fees/{id}/` | DELETE | Delete a calculator fee |
| `/api/calculator/application-fees/` | GET | List all application fees |
| `/api/calculator/application-fees/` | POST | Create a new application fee |
| `/api/calculator/application-fees/{id}/` | GET | Get application fee details |
| `/api/calculator/application-fees/{id}/` | PUT | Update an application fee |
| `/api/calculator/application-fees/{id}/` | PATCH | Partially update an application fee |
| `/api/calculator/application-fees/{id}/` | DELETE | Delete an application fee |
| `/api/calculator/application-fees/{id}/waive/` | POST | Waive a fee for an application |

## Notification APIs

| Exact API Path | HTTP Method | Description |
|----------------|-------------|-------------|
| `/api/notifications/` | GET | List all notifications for the current user |
| `/api/notifications/` | POST | Create a new notification |
| `/api/notifications/{id}/` | GET | Get notification details |
| `/api/notifications/{id}/` | PUT | Update a notification |
| `/api/notifications/{id}/` | PATCH | Partially update a notification |
| `/api/notifications/{id}/` | DELETE | Delete a notification |
| `/api/notifications/unread/` | GET | Get all unread notifications for the current user |
| `/api/notes/` | GET | List all notes |
| `/api/notes/` | POST | Create a new note |
| `/api/notes/{id}/` | GET | Get note details |
| `/api/notes/{id}/` | PUT | Update a note |
| `/api/notes/{id}/` | PATCH | Partially update a note |
| `/api/notes/{id}/` | DELETE | Delete a note |

## Product APIs

| Exact API Path | HTTP Method | Description |
|----------------|-------------|-------------|
| `/api/products/` | GET | List all products |
| `/api/products/` | POST | Create a new product |
| `/api/products/{id}/` | GET | Get product details |
| `/api/products/{id}/` | PUT | Update a product |
| `/api/products/{id}/` | PATCH | Partially update a product |
| `/api/products/{id}/` | DELETE | Delete a product |

## Filter Parameters

Many API endpoints support filtering, searching, and ordering. Here are the supported parameters for each endpoint:

### Documents

- **Filter fields**: `document_type`, `category`, `status`, `application`, `is_confidential`, `is_favorite`, `is_pinned`, `created_by`, `updated_by`, `created_at_after`, `created_at_before`, `updated_at_after`, `updated_at_before`
- **Search fields**: `title`, `description`, `keywords`, `content` (full-text search)
- **Ordering fields**: `title`, `created_at`, `updated_at`, `status`, `document_type`

### Applications

- **Filter fields**: `status`, `stage`, `borrower`, `broker`, `product`
- **Search fields**: `borrower__first_name`, `borrower__last_name`, `borrower__email`
- **Ordering fields**: `created_at`, `updated_at`, `status`, `stage`

### Borrowers

- **Filter fields**: `state`, `created_at`
- **Search fields**: `first_name`, `last_name`, `email`, `phone_number`
- **Ordering fields**: `created_at`, `first_name`, `last_name`

### Brokers

- **Filter fields**: `created_at`
- **Search fields**: `first_name`, `last_name`, `email`, `phone_number`, `company_name`
- **Ordering fields**: `created_at`, `first_name`, `last_name`, `company_name`

### Calculator Fees

- **Filter fields**: `fee_type`, `is_active`, `products`
- **Search fields**: `name`, `description`
- **Ordering fields**: `name`, `amount`, `created_at`

### Notifications

- **Filter fields**: `type`, `sent_status`, `related_application`
- **Search fields**: `message`
- **Ordering fields**: `trigger_date`, `created_at`

### Notes

- **Filter fields**: `application`, `user`, `reminder_date`
- **Search fields**: `content`
- **Ordering fields**: `created_at`, `reminder_date`

### Products

- **Search fields**: `name`, `description`
- **Ordering fields**: `name`, `created_at`
