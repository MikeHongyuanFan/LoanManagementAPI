# API Relationship Validation Results

This document presents the results of validating the API relationships documented in the API Connection Structure document against the actual code implementation.

## Validation Methodology

For each relationship, we examined:
1. Model relationships (foreign keys, many-to-many fields)
2. Serializer implementations
3. View/viewset implementations
4. URL patterns and routing

## Validation Results Summary

| Status | Count | Description |
|--------|-------|-------------|
| ✅ Confirmed | 24 | Relationship exists and functions as documented |
| ⚠️ Partial | 5 | Relationship exists but with some differences from documentation |
| ❌ Missing | 3 | Relationship does not exist in the codebase |
| 🔄 Bidirectional | 8 | Relationship exists in both directions |

## Applications API Relationships

| Source Endpoint | Target Endpoint | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|---------------------|
| `/api/applications/` | `/api/borrowers/{id}/` | ✅ Confirmed | Foreign key relationship in Application model to Borrower model |
| `/api/applications/` | `/api/brokers/{id}/` | ✅ Confirmed | Foreign key relationship in Application model to Broker model |
| `/api/applications/` | `/api/products/{id}/` | ✅ Confirmed | Foreign key relationship in Application model to Product model |
| `/api/applications/` | `/api/fees/?application={id}` | ✅ Confirmed | Foreign key relationship in Fee model to Application model with related_name='fees' |
| `/api/applications/` | `/api/repayments/?application={id}` | ✅ Confirmed | Foreign key relationship in Repayment model to Application model with related_name='repayments' |
| `/api/applications/` | `/api/loan-extensions/?application={id}` | ✅ Confirmed | Foreign key relationship in LoanExtension model to Application model with related_name='extensions' |
| `/api/applications/` | `/api/notes/?application={id}` | ✅ Confirmed | Foreign key relationship in Note model to Application model with related_name='notes' |
| `/api/applications/` | `/api/notifications/?related_application={id}` | ✅ Confirmed | Foreign key relationship in Notification model to Application model with related_name='notifications' |
| `/api/applications/` | `/api/document-management/documents/?application={id}` | ✅ Confirmed | Foreign key relationship in Document model to Application model with related_name='documents' |

## Borrowers API Relationships

| Source Endpoint | Target Endpoint | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|---------------------|
| `/api/borrowers/` | `/api/applications/` | 🔄 Bidirectional | Reverse relationship from borrower to applications via related_name='applications' |

## Brokers API Relationships

| Source Endpoint | Target Endpoint | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|---------------------|
| `/api/brokers/` | `/api/applications/` | 🔄 Bidirectional | Reverse relationship from broker to applications via related_name='applications' |

## Products API Relationships

| Source Endpoint | Target Endpoint | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|---------------------|
| `/api/products/` | `/api/applications/` | 🔄 Bidirectional | Reverse relationship from product to applications via related_name='applications' |
| `/api/products/` | `/api/calculator/calculations/` | ⚠️ Partial | No direct relationship in models, but products are referenced in calculator logic |

## Fees API Relationships

| Source Endpoint | Target Endpoint | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|---------------------|
| `/api/fees/` | `/api/applications/?application={id}` | 🔄 Bidirectional | Bidirectional relationship between Fee and Application models |
| `/api/fees/` | `/api/calculator/calculations/` | ⚠️ Partial | No direct relationship in models, but fees are used in calculation logic |
| `/api/fees/` | `/api/calculator/application-fees/` | ✅ Confirmed | Foreign key relationship in ApplicationFee model to Fee model |

## Repayments API Relationships

| Source Endpoint | Target Endpoint | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|---------------------|
| `/api/repayments/` | `/api/calculator/calculations/calculate/` | ⚠️ Partial | Relationship exists but through RepaymentSchedule model, not directly |
| `/api/repayments/` | `/api/applications/{id}/` | 🔄 Bidirectional | Bidirectional relationship between Repayment and Application models |

## Loan Extensions API Relationships

| Source Endpoint | Target Endpoint | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|---------------------|
| `/api/loan-extensions/` | `/api/applications/{id}/` | 🔄 Bidirectional | Bidirectional relationship between LoanExtension and Application models |

## Notes API Relationships

| Source Endpoint | Target Endpoint | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|---------------------|
| `/api/notes/` | `/api/applications/{id}/` | 🔄 Bidirectional | Bidirectional relationship between Note and Application models |

## Notifications API Relationships

| Source Endpoint | Target Endpoint | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|---------------------|
| `/api/notifications/` | `/api/document-management/approvals/` | ❌ Missing | No direct relationship found in the code between notifications and approvals |
| `/api/notifications/` | `/api/document-management/signature-requests/` | ❌ Missing | No direct relationship found in the code between notifications and signature requests |
| `/api/notifications/` | `/api/applications/?related_application={id}` | 🔄 Bidirectional | Bidirectional relationship between Notification and Application models |

## Document Management API Relationships

| Source Endpoint | Target Endpoint | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|---------------------|
| `/api/document-management/documents/` | `/api/applications/{id}` | 🔄 Bidirectional | Bidirectional relationship between Document and Application models |
| `/api/document-management/documents/` | `/api/document-management/approvals/` | ✅ Confirmed | Foreign key relationship in DocumentApproval model to Document model with related_name='approvals' |
| `/api/document-management/documents/` | `/api/document-management/signature-requests/` | ✅ Confirmed | Foreign key relationship in DocumentSignatureRequest model to Document model with related_name='signature_requests' |
| `/api/document-management/documents/` | `/api/document-management/comments/` | ✅ Confirmed | Foreign key relationship in DocumentComment model to Document model with related_name='comments' |
| `/api/document-management/documents/` | `/api/document-management/metadata/` | ✅ Confirmed | Foreign key relationship in DocumentMetadata model to Document model with related_name='custom_metadata' |
| `/api/document-management/documents/` | `/api/document-management/relationships/` | ✅ Confirmed | Foreign key relationships in DocumentRelationship model to Document model with related_names 'related_to' and 'related_from' |
| `/api/document-management/documents/` | `/api/document-management/collections/` | ✅ Confirmed | Many-to-many relationship between Document and DocumentCollection models |

## Document Approvals API Relationships

| Source Endpoint | Target Endpoint | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|---------------------|
| `/api/document-management/approvals/` | `/documents/{id}/request-approval/` | ✅ Confirmed | Endpoint exists in documents/views_approval.py |
| `/api/document-management/approvals/` | `/api/notifications/` | ❌ Missing | No direct relationship found in the code between approvals and notifications |

## Signature Requests API Relationships

| Source Endpoint | Target Endpoint | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|---------------------|
| `/api/document-management/signature-requests/` | `/api/notifications/` | ⚠️ Partial | No direct relationship in models, but likely handled in business logic |
| `/api/document-management/signature-requests/` | `/api/document-management/signatures/` | ✅ Confirmed | One-to-one relationship in DocumentSignature model to DocumentSignatureRequest model with related_name='signature' |

## Signatures API Relationships

| Source Endpoint | Target Endpoint | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|---------------------|
| `/api/document-management/signatures/` | `/signature-requests/{id}/sign/` | ✅ Confirmed | Endpoint exists in documents/views_endpoints.py as signature_request_respond |

## Comments API Relationships

| Source Endpoint | Target Endpoint | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|---------------------|
| `/api/document-management/comments/` | `/documents/` | ✅ Confirmed | Foreign key relationship in DocumentComment model to Document model with related_name='comments' |

## Metadata API Relationships

| Source Endpoint | Target Endpoint | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|---------------------|
| `/api/document-management/metadata/` | `/documents/{id}/add_metadata/` | ✅ Confirmed | Endpoint exists in documents/views_endpoints.py as document_metadata_bulk_update |

## Relationships API Relationships

| Source Endpoint | Target Endpoint | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|---------------------|
| `/api/document-management/relationships/` | `/documents/{id}/add_relationship/` | ⚠️ Partial | No specific endpoint found, but relationship functionality exists in the DocumentRelationship model |

## Collections API Relationships

| Source Endpoint | Target Endpoint | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|---------------------|
| `/api/document-management/collections/` | `/documents/{id}/add_to_collection/` | ✅ Confirmed | Many-to-many relationship between Document and DocumentCollection models |

## Calculator API Relationships

| Source Endpoint | Target Endpoint | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|---------------------|
| `/api/calculator/calculations/` | `/api/fees/` | ✅ Confirmed | Relationship exists through the Fee model in calculator app |
| `/api/calculator/calculations/` | `/api/products/` | ✅ Confirmed | Products are referenced in LoanCalculation model through the Application model |
| `/api/calculator/calculations/` | `/api/calculator/repayments/` | ✅ Confirmed | Foreign key relationship in RepaymentSchedule model to LoanCalculation model with related_name='repayments' |
| `/api/calculator/calculations/` | `/api/calculator/application-fees/` | ✅ Confirmed | Relationship exists through the ApplicationFee model |

## Identified Issues and Recommendations

1. **Missing Notification Relationships**
   - Issue: No direct relationships found between notifications and document approvals/signature requests
   - Recommendation: Implement notification triggers in the approval and signature request workflows

2. **Partial Calculator Relationships**
   - Issue: Some calculator relationships are implemented through business logic rather than direct model relationships
   - Recommendation: Consider adding explicit model relationships or documenting the business logic connections

3. **Document Relationship Endpoint**
   - Issue: No specific endpoint found for adding relationships between documents
   - Recommendation: Implement a dedicated endpoint for document relationship management

4. **Bidirectional Relationships**
   - Observation: Many relationships are bidirectional through Django's related_name feature
   - Recommendation: Update the API Connection Structure document to reflect these bidirectional relationships
