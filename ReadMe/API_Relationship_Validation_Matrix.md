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
| `/api/applications/` | `/api/borrowers/{id}/` | Uses | ⏳ Pending | When creating/updating an application, a borrower ID must be linked |
| `/api/applications/` | `/api/brokers/{id}/` | Uses | ⏳ Pending | Broker data is linked to track which staff or third-party referred or manages this application |
| `/api/applications/` | `/api/products/{id}/` | Uses | ⏳ Pending | The selected loan product determines base interest rate, terms, and product-based fees |
| `/api/applications/` | `/api/fees/?application={id}` | Links to | ⏳ Pending | Fetches all fees that apply specifically to this application |
| `/api/applications/` | `/api/repayments/?application={id}` | Links to | ⏳ Pending | Retrieves all repayment entries tied to the loan |
| `/api/applications/` | `/api/loan-extensions/?application={id}` | Links to | ⏳ Pending | Allows clients to request or view previous loan extensions |
| `/api/applications/` | `/api/notes/?application={id}` | Links to | ⏳ Pending | Internal staff notes attached to the application |
| `/api/applications/` | `/api/notifications/?related_application={id}` | Triggers | ⏳ Pending | Notification service sends alerts when an application's status changes |
| `/api/applications/` | `/api/document-management/documents/?application={id}` | Links to | ⏳ Pending | Upload and manage documents bound to an application |

## Borrowers API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/borrowers/` | `/api/applications/` | Used by | ⏳ Pending | Applications must include a borrower ID |

## Brokers API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/brokers/` | `/api/applications/` | Used by | ⏳ Pending | Brokers are assigned to applications for referral tracking |

## Products API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/products/` | `/api/applications/` | Used by | ⏳ Pending | The selected product defines the structure and rules of a loan |
| `/api/products/` | `/api/calculator/calculations/` | Used by | ⏳ Pending | The calculator engine pulls parameters from the product |

## Fees API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/fees/` | `/api/applications/?application={id}` | Used by | ⏳ Pending | Lists current or pending fees against an application |
| `/api/fees/` | `/api/calculator/calculations/` | Used by | ⏳ Pending | Fee data is required for repayment projections |
| `/api/fees/` | `/api/calculator/application-fees/` | Linked to | ⏳ Pending | Stores applied fees on a per-application basis |

## Repayments API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/repayments/` | `/api/calculator/calculations/calculate/` | Created by | ⏳ Pending | After a loan term is calculated, a schedule of repayment is generated |
| `/api/repayments/` | `/api/applications/{id}/` | Queried by | ⏳ Pending | Application detail views will list repayment history and future schedule |

## Loan Extensions API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/loan-extensions/` | `/api/applications/{id}/` | Queried by | ⏳ Pending | Displays all extensions tied to the loan |

## Notes API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/notes/` | `/api/applications/{id}/` | Linked to | ⏳ Pending | Used by staff to annotate application files |

## Notifications API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/notifications/` | `/api/document-management/approvals/` | Triggered by | ⏳ Pending | Sends alerts to reviewers when document approval actions occur |
| `/api/notifications/` | `/api/document-management/signature-requests/` | Triggered by | ⏳ Pending | Sends alerts to signees when they're assigned |
| `/api/notifications/` | `/api/applications/?related_application={id}` | Linked to | ⏳ Pending | Events like application submission generate notifications |

## Document Management API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/document-management/documents/` | `/api/applications/{id}` | Linked to | ⏳ Pending | Documents are tagged to applications during upload |
| `/api/document-management/documents/` | `/api/document-management/approvals/` | Triggers | ⏳ Pending | Users can request internal approvals via API call |
| `/api/document-management/documents/` | `/api/document-management/signature-requests/` | Triggers | ⏳ Pending | Initiates electronic signing for selected users |
| `/api/document-management/documents/` | `/api/document-management/comments/` | Uses | ⏳ Pending | Allows inline discussion and annotations |
| `/api/document-management/documents/` | `/api/document-management/metadata/` | Uses | ⏳ Pending | Metadata fields are attached |
| `/api/document-management/documents/` | `/api/document-management/relationships/` | Uses | ⏳ Pending | Related documents can be linked for workflow automation |
| `/api/document-management/documents/` | `/api/document-management/collections/` | Uses | ⏳ Pending | Documents can be grouped under folders |

## Document Approvals API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/document-management/approvals/` | `/documents/{id}/request-approval/` | Triggered by | ⏳ Pending | Starts a review and sign-off process |
| `/api/document-management/approvals/` | `/api/notifications/` | Triggers | ⏳ Pending | Reviewer is notified once approval is pending |

## Signature Requests API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/document-management/signature-requests/` | `/api/notifications/` | Triggers | ⏳ Pending | Email + in-app alert to notify that a signature is pending |
| `/api/document-management/signature-requests/` | `/api/document-management/signatures/` | Confirms via | ⏳ Pending | Once signed, the result is logged |

## Signatures API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/document-management/signatures/` | `/signature-requests/{id}/sign/` | Created by | ⏳ Pending | Stores proof of digital signature |

## Comments API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/document-management/comments/` | `/documents/` | Attached to | ⏳ Pending | Stores comment threads and change requests |

## Metadata API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/document-management/metadata/` | `/documents/{id}/add_metadata/` | Used by | ⏳ Pending | Adds detailed tag data to support filtering |

## Relationships API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/document-management/relationships/` | `/documents/{id}/add_relationship/` | Used by | ⏳ Pending | Builds references between related documents |

## Collections API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/document-management/collections/` | `/documents/{id}/add_to_collection/` | Used by | ⏳ Pending | Folders for managing large sets of files |

## Templates API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/document-management/templates/` | Document creation | Used during | ⏳ Pending | Format templates like standard contracts |

## Calculator API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/calculator/calculations/` | `/api/fees/` | Uses | ⏳ Pending | Fee data is included in cost projection |
| `/api/calculator/calculations/` | `/api/products/` | Uses | ⏳ Pending | Product terms are required |
| `/api/calculator/calculations/` | `/api/calculator/repayments/` | Outputs to | ⏳ Pending | Generates complete repayment schedule |
| `/api/calculator/calculations/` | `/api/calculator/application-fees/` | Creates | ⏳ Pending | Stores calculated fees per application |

## Calculator Repayments API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/calculator/repayments/` | `/api/calculator/calculations/` | Created by | ⏳ Pending | Amortization schedule is saved post-calculation |

## Calculator Application Fees API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/calculator/application-fees/` | `/api/fees/` | Created from | ⏳ Pending | Each instance of a fee applied to an app is saved here |

## Calculator Fees API Relationships

| Source Endpoint | Target Endpoint | Relationship Type | Validation Status | Implementation Notes |
|-----------------|----------------|-------------------|-------------------|---------------------|
| `/api/calculator/fees/` | `/api/calculator/calculations/` | Used by | ⏳ Pending | Input into simulation model |
