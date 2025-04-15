# API Relationship Validation Matrix

This document tracks the validation status of all API relationships documented in the API Connection Structure document.

## Validation Status Legend
- ⏳ **Pending**: Relationship has not been validated yet
- ✅ **Confirmed**: Relationship exists and functions as documented
- ⚠️ **Partial**: Relationship exists but with some differences from documentation
- ❌ **Missing**: Relationship does not exist in the codebase
- 🔄 **Bidirectional**: Relationship exists in both directions

## Applications API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/applications/` | `/api/borrowers/{id}/` | Uses | ✅ Confirmed | Foreign key relationship in Application model to Borrower model |
| `/api/applications/` | `/api/brokers/{id}/` | Uses | ✅ Confirmed | Foreign key relationship in Application model to Broker model |
| `/api/applications/` | `/api/products/{id}/` | Uses | ✅ Confirmed | Foreign key relationship in Application model to Product model |
| `/api/applications/` | `/api/fees/?application={id}` | Links to | ✅ Confirmed | Foreign key relationship in Fee model to Application model with related_name='fees' |
| `/api/applications/` | `/api/repayments/?application={id}` | Links to | ✅ Confirmed | Foreign key relationship in Repayment model to Application model with related_name='repayments' |
| `/api/applications/` | `/api/loan-extensions/?application={id}` | Links to | ✅ Confirmed | Foreign key relationship in LoanExtension model to Application model with related_name='extensions' |
| `/api/applications/` | `/api/notes/?application={id}` | Links to | ✅ Confirmed | Foreign key relationship in Note model to Application model with related_name='notes' |
| `/api/applications/` | `/api/notifications/?related_application={id}` | Triggers | ✅ Confirmed | Foreign key relationship in Notification model to Application model with related_name='notifications' |
| `/api/applications/` | `/api/document-management/documents/?application={id}` | Links to | ✅ Confirmed | Foreign key relationship in Document model to Application model with related_name='documents' |

## Borrowers API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/borrowers/` | `/api/applications/` | Used by | ✅ Confirmed | Bidirectional relationship from borrower to applications via related_name='applications' |

## Brokers API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/brokers/` | `/api/applications/` | Used by | ✅ Confirmed | Bidirectional relationship from broker to applications via related_name='applications' |

## Products API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/products/` | `/api/applications/` | Used by | ✅ Confirmed | Bidirectional relationship from product to applications via related_name='applications' |
| `/api/products/` | `/api/calculator/calculations/` | Used by | ✅ Confirmed | Direct relationship added in LoanCalculation model with product field |

## Fees API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/fees/` | `/api/applications/?application={id}` | Used by | ✅ Confirmed | Bidirectional relationship between Fee and Application models |
| `/api/fees/` | `/api/calculator/calculations/` | Used by | ✅ Confirmed | Direct ManyToMany relationship through calculations field in Fee model |
| `/api/fees/` | `/api/calculator/application-fees/` | Linked to | ✅ Confirmed | Foreign key relationship in ApplicationFee model to Fee model with related_name='application_fees' |

## Repayments API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/repayments/` | `/api/calculator/calculations/calculate/` | Created by | ✅ Confirmed | Direct relationship through RepaymentSchedule model with calculation field |
| `/api/repayments/` | `/api/applications/{id}/` | Queried by | ✅ Confirmed | Bidirectional relationship between Repayment and Application models |

## Loan Extensions API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/loan-extensions/` | `/api/applications/{id}/` | Queried by | ✅ Confirmed | Bidirectional relationship between LoanExtension and Application models |

## Notes API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/notes/` | `/api/applications/{id}/` | Linked to | ✅ Confirmed | Bidirectional relationship between Note and Application models |

## Notifications API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/notifications/` | `/api/document-management/approvals/` | Triggered by | ✅ Confirmed | Implemented through notification service with create_document_approval_notification function |
| `/api/notifications/` | `/api/document-management/signature-requests/` | Triggered by | ✅ Confirmed | Implemented through notification service with create_signature_request_notification function |
| `/api/notifications/` | `/api/applications/?related_application={id}` | Linked to | ✅ Confirmed | Bidirectional relationship between Notification and Application models |

## Document Management API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/document-management/documents/` | `/api/applications/{id}` | Linked to | ✅ Confirmed | Bidirectional relationship between Document and Application models |
| `/api/document-management/documents/` | `/api/document-management/approvals/` | Triggers | ✅ Confirmed | Foreign key relationship in DocumentApproval model to Document model with related_name='approvals' |
| `/api/document-management/documents/` | `/api/document-management/signature-requests/` | Triggers | ✅ Confirmed | Foreign key relationship in DocumentSignatureRequest model to Document model with related_name='signature_requests' |
| `/api/document-management/documents/` | `/api/document-management/comments/` | Uses | ✅ Confirmed | Foreign key relationship in DocumentComment model to Document model with related_name='comments' |
| `/api/document-management/documents/` | `/api/document-management/metadata/` | Uses | ✅ Confirmed | Foreign key relationship in DocumentMetadata model to Document model with related_name='custom_metadata' |
| `/api/document-management/documents/` | `/api/document-management/relationships/` | Uses | ✅ Confirmed | Foreign key relationships in DocumentRelationship model to Document model with related_names 'related_to' and 'related_from' |
| `/api/document-management/documents/` | `/api/document-management/collections/` | Uses | ✅ Confirmed | Many-to-many relationship between Document and DocumentCollection models |

## Document Approvals API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/document-management/approvals/` | `/documents/{id}/request-approval/` | Triggered by | ✅ Confirmed | Endpoint exists in documents/views_approval.py |
| `/api/document-management/approvals/` | `/api/notifications/` | Triggers | ✅ Confirmed | Implemented through notification service with create_document_approval_notification function |

## Signature Requests API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/document-management/signature-requests/` | `/api/notifications/` | Triggers | ✅ Confirmed | Implemented through notification service with create_signature_request_notification function |
| `/api/document-management/signature-requests/` | `/api/document-management/signatures/` | Confirms via | ✅ Confirmed | One-to-one relationship in DocumentSignature model to DocumentSignatureRequest model with related_name='signature' |

## Signatures API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/document-management/signatures/` | `/signature-requests/{id}/sign/` | Created by | ✅ Confirmed | Endpoint exists in documents/views_endpoints.py as signature_request_respond |

## Comments API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/document-management/comments/` | `/documents/` | Attached to | ✅ Confirmed | Foreign key relationship in DocumentComment model to Document model with related_name='comments' |

## Metadata API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/document-management/metadata/` | `/documents/{id}/add_metadata/` | Used by | ✅ Confirmed | Endpoint exists in documents/views_endpoints.py as document_metadata_bulk_update |

## Relationships API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/document-management/relationships/` | `/documents/{id}/add_relationship/` | Used by | ✅ Confirmed | Implemented through custom actions in DocumentViewSet and DocumentRelationshipViewSet |

## Collections API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/document-management/collections/` | `/documents/{id}/add_to_collection/` | Used by | ✅ Confirmed | Many-to-many relationship between Document and DocumentCollection models |

## Templates API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/document-management/templates/` | Document creation | Used during | ✅ Confirmed | Templates are used during document creation process |

## Calculator API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/calculator/calculations/` | `/api/fees/` | Uses | ✅ Confirmed | Relationship exists through the Fee model in calculator app |
| `/api/calculator/calculations/` | `/api/products/` | Uses | ✅ Confirmed | Direct relationship added in LoanCalculation model with product field |
| `/api/calculator/calculations/` | `/api/calculator/repayments/` | Outputs to | ✅ Confirmed | Foreign key relationship in RepaymentSchedule model to LoanCalculation model with related_name='repayments' |
| `/api/calculator/calculations/` | `/api/calculator/application-fees/` | Creates | ✅ Confirmed | Direct relationship added in ApplicationFee model with calculation field |

## Calculator Repayments API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/calculator/repayments/` | `/api/calculator/calculations/` | Created by | ✅ Confirmed | Foreign key relationship in RepaymentSchedule model to LoanCalculation model |

## Calculator Application Fees API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/calculator/application-fees/` | `/api/fees/` | Created from | ✅ Confirmed | Foreign key relationship in ApplicationFee model to Fee model |
| `/api/calculator/application-fees/` | `/api/calculator/calculations/` | Created by | ✅ Confirmed | Direct relationship added in ApplicationFee model with calculation field |

## Calculator Fees API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/calculator/fees/` | `/api/calculator/calculations/` | Used by | ⚠️ Partial | Relationship exists through business logic in calculation service and ManyToMany field in Fee model |
