# API Endpoint Inventory

This document provides a comprehensive inventory of all implemented API endpoints in the CRM Loan Management System, categorized by service domain.

## Table of Contents
- [Applications](#applications)
- [Borrowers](#borrowers)
- [Brokers](#brokers)
- [Products](#products)
- [Calculator](#calculator)
- [Document Management](#document-management)
- [Notifications](#notifications)
- [Dashboard](#dashboard)

---

## Applications

| Endpoint | HTTP Methods | Description | Input Data | Output Data |
|----------|--------------|-------------|------------|-------------|
| `/api/applications/` | GET, POST | List all applications or create a new one | Application data including borrower_id, product_id, broker_id (optional) | List of applications or created application details |
| `/api/applications/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete an application | Updated application data | Application details |
| `/api/valuers/` | GET, POST | List all valuers or create a new one | Valuer data | List of valuers or created valuer details |
| `/api/valuers/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete a valuer | Updated valuer data | Valuer details |
| `/api/qs/` | GET, POST | List all quantity surveyors or create a new one | QS data | List of quantity surveyors or created QS details |
| `/api/qs/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete a quantity surveyor | Updated QS data | QS details |
| `/api/referrals/` | GET, POST | List all referrals or create a new one | Referral data | List of referrals or created referral details |
| `/api/referrals/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete a referral | Updated referral data | Referral details |
| `/api/fees/` | GET, POST | List all fees or create a new one | Fee data | List of fees or created fee details |
| `/api/fees/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete a fee | Updated fee data | Fee details |
| `/api/repayments/` | GET, POST | List all repayments or create a new one | Repayment data | List of repayments or created repayment details |
| `/api/repayments/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete a repayment | Updated repayment data | Repayment details |
| `/api/loan-extensions/` | GET, POST | List all loan extensions or create a new one | Loan extension data | List of loan extensions or created loan extension details |
| `/api/loan-extensions/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete a loan extension | Updated loan extension data | Loan extension details |

## Borrowers

| Endpoint | HTTP Methods | Description | Input Data | Output Data |
|----------|--------------|-------------|------------|-------------|
| `/api/borrowers/` | GET, POST | List all borrowers or create a new one | Borrower data | List of borrowers or created borrower details |
| `/api/borrowers/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete a borrower | Updated borrower data | Borrower details |

## Brokers

| Endpoint | HTTP Methods | Description | Input Data | Output Data |
|----------|--------------|-------------|------------|-------------|
| `/api/brokers/` | GET, POST | List all brokers or create a new one | Broker data | List of brokers or created broker details |
| `/api/brokers/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete a broker | Updated broker data | Broker details |

## Products

| Endpoint | HTTP Methods | Description | Input Data | Output Data |
|----------|--------------|-------------|------------|-------------|
| `/api/products/` | GET, POST | List all products or create a new one | Product data | List of products or created product details |
| `/api/products/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete a product | Updated product data | Product details |
| `/api/products/{product_id}/fees/` | GET, POST | List all fees for a product or create a new one | Fee data | List of fees or created fee details |
| `/api/products/{product_id}/fees/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete a fee for a product | Updated fee data | Fee details |

## Calculator

| Endpoint | HTTP Methods | Description | Input Data | Output Data |
|----------|--------------|-------------|------------|-------------|
| `/api/calculator/calculations/` | GET, POST | List all calculations or create a new one | Calculation parameters | List of calculations or calculation results |
| `/api/calculator/calculations/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete a calculation | Updated calculation parameters | Calculation details |
| `/api/calculator/repayments/` | GET, POST | List all repayment schedules or create a new one | Repayment schedule parameters | List of repayment schedules or created schedule details |
| `/api/calculator/repayments/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete a repayment schedule | Updated repayment schedule parameters | Repayment schedule details |
| `/api/calculator/fees/` | GET, POST | List all calculator fees or create a new one | Fee data | List of fees or created fee details |
| `/api/calculator/fees/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete a calculator fee | Updated fee data | Fee details |
| `/api/calculator/application-fees/` | GET, POST | List all application fees or create a new one | Application fee data | List of application fees or created application fee details |
| `/api/calculator/application-fees/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete an application fee | Updated application fee data | Application fee details |
| `/api/calculator/monthly-payment/` | POST | Calculate monthly payment | Loan amount, interest rate, term | Monthly payment amount |
| `/api/calculator/amortization-schedule/` | POST | Generate amortization schedule | Loan amount, interest rate, term | Complete amortization schedule |
| `/api/calculator/loan-summary/` | POST | Generate loan summary | Loan parameters | Summary of loan costs and payments |
| `/api/calculator/product-payment/` | POST | Calculate payment for a specific product | Product ID, loan amount | Payment details for the product |
| `/api/calculator/compare-products/` | POST | Compare multiple products | List of product IDs, loan amount | Comparison of products |
| `/api/calculator/affordability/` | POST | Calculate affordability | Income, expenses, other debts | Maximum affordable loan amount |

## Document Management

| Endpoint | HTTP Methods | Description | Input Data | Output Data |
|----------|--------------|-------------|------------|-------------|
| `/api/document-management/documents/` | GET, POST | List all documents or create a new one | Document data | List of documents or created document details |
| `/api/document-management/documents/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete a document | Updated document data | Document details |
| `/api/document-management/categories/` | GET, POST | List all document categories or create a new one | Category data | List of categories or created category details |
| `/api/document-management/categories/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete a document category | Updated category data | Category details |
| `/api/document-management/templates/` | GET, POST | List all document templates or create a new one | Template data | List of templates or created template details |
| `/api/document-management/templates/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete a document template | Updated template data | Template details |
| `/api/document-management/comments/` | GET, POST | List all document comments or create a new one | Comment data | List of comments or created comment details |
| `/api/document-management/comments/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete a document comment | Updated comment data | Comment details |
| `/api/document-management/approvals/` | GET, POST | List all document approvals or create a new one | Approval data | List of approvals or created approval details |
| `/api/document-management/approvals/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete a document approval | Updated approval data | Approval details |
| `/api/document-management/signature-requests/` | GET, POST | List all signature requests or create a new one | Signature request data | List of signature requests or created request details |
| `/api/document-management/signature-requests/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete a signature request | Updated signature request data | Signature request details |
| `/api/document-management/signatures/` | GET, POST | List all signatures or create a new one | Signature data | List of signatures or created signature details |
| `/api/document-management/signatures/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete a signature | Updated signature data | Signature details |
| `/api/document-management/collections/` | GET, POST | List all document collections or create a new one | Collection data | List of collections or created collection details |
| `/api/document-management/collections/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete a document collection | Updated collection data | Collection details |
| `/api/document-management/relationships/` | GET, POST | List all document relationships or create a new one | Relationship data | List of relationships or created relationship details |
| `/api/document-management/relationships/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete a document relationship | Updated relationship data | Relationship details |
| `/api/document-management/metadata-fields/` | GET, POST | List all metadata fields or create a new one | Metadata field data | List of metadata fields or created field details |
| `/api/document-management/metadata-fields/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete a metadata field | Updated metadata field data | Metadata field details |
| `/api/document-management/document-metadata/` | GET, POST | List all document metadata or create a new one | Document metadata data | List of document metadata or created metadata details |
| `/api/document-management/document-metadata/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete document metadata | Updated document metadata data | Document metadata details |
| `/api/document-management/documents/{id}/update-metadata/` | POST | Update metadata for a document | Metadata key-value pairs | Updated document with metadata |
| `/api/document-management/signature-requests/{id}/respond/` | POST | Respond to a signature request | Response data (approve/reject) | Updated signature request |
| `/api/document-management/documents/{id}/request-approval/` | POST | Request approval for a document | Approval request data | Created approval request |
| `/api/document-management/approvals/{id}/respond/` | POST | Respond to an approval request | Response data (approve/reject) | Updated approval request |
| `/api/document-management/approvals/{id}/cancel/` | POST | Cancel an approval request | - | Cancelled approval request |
| `/api/document-management/approvals/{id}/reassign/` | POST | Reassign an approval request | New assignee data | Reassigned approval request |
| `/api/document-management/documents/{id}/create-version/` | POST | Create a new version of a document | Document content | Created document version |
| `/api/document-management/documents/{id}/versions/` | GET | Get all versions of a document | - | List of document versions |
| `/api/document-management/documents/{id}/revert/{version_id}/` | POST | Revert a document to a previous version | - | Updated document |
| `/api/document-management/versions/compare/{version1_id}/{version2_id}/` | GET | Compare two document versions | - | Comparison results |
| `/api/document-management/search/` | GET | Advanced document search | Search parameters | Search results |
| `/api/document-management/search/full-text/` | GET | Full-text document search | Search query | Search results |
| `/api/document-management/documents/recent/` | GET | Get recent documents | - | List of recent documents |
| `/api/document-management/documents/suggestions/` | GET | Get document suggestions | Query parameters | List of suggested documents |

## Notifications

| Endpoint | HTTP Methods | Description | Input Data | Output Data |
|----------|--------------|-------------|------------|-------------|
| `/api/notifications/` | GET, POST | List all notifications or create a new one | Notification data | List of notifications or created notification details |
| `/api/notifications/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete a notification | Updated notification data | Notification details |
| `/api/notes/` | GET, POST | List all notes or create a new one | Note data | List of notes or created note details |
| `/api/notes/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete a note | Updated note data | Note details |

## Dashboard

| Endpoint | HTTP Methods | Description | Input Data | Output Data |
|----------|--------------|-------------|------------|-------------|
| `/api/dashboard/metrics/` | GET, POST | List all dashboard metrics or create a new one | Metric data | List of metrics or created metric details |
| `/api/dashboard/metrics/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete a dashboard metric | Updated metric data | Metric details |
| `/api/dashboard/widgets/` | GET, POST | List all dashboard widgets or create a new one | Widget data | List of widgets or created widget details |
| `/api/dashboard/widgets/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete a dashboard widget | Updated widget data | Widget details |
| `/api/dashboard/layouts/` | GET, POST | List all dashboard layouts or create a new one | Layout data | List of layouts or created layout details |
| `/api/dashboard/layouts/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete a dashboard layout | Updated layout data | Layout details |
| `/api/dashboard/preferences/` | GET, POST | List all user dashboard preferences or create a new one | Preference data | List of preferences or created preference details |
| `/api/dashboard/preferences/{id}/` | GET, PUT, PATCH, DELETE | Retrieve, update or delete a user dashboard preference | Updated preference data | Preference details |
| `/api/dashboard/overview/` | GET | Get dashboard overview | Filter parameters | Dashboard overview data |
| `/api/dashboard/applications/` | GET | Get application dashboard | Filter parameters | Application dashboard data |
| `/api/dashboard/documents/` | GET | Get document dashboard | Filter parameters | Document dashboard data |
| `/api/dashboard/entities/` | GET | Get borrower/broker dashboard | Filter parameters | Entity dashboard data |
