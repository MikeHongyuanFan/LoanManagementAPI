# Integration Testing for Loan Management API

This directory contains integration tests that verify the interaction between multiple components of the Loan Management API system. These tests ensure that different parts of the system work together correctly in real-world scenarios.

## Test Coverage

The integration tests focus on the following key workflows and component interactions:

### 1. Loan Application Workflow
- Complete loan application process from submission to approval
- Integration between applications, borrowers, products, and documents
- Loan calculation and fee calculation
- Document approval workflow
- Application status updates

### 2. Document Management Workflow
- Document approval process
- Electronic signature workflow
- Notification system integration
- Relationship between documents, approvals, signatures, and notifications

### 3. Calculator Component Integration
- Integration between calculator, products, and fees
- Fee calculation based on product and loan amount
- Repayment schedule generation
- Relationship integrity between all calculator components

## Running the Tests

To run these integration tests:

```bash
# Run all integration tests
python manage.py test Testing.Stage7_IntegrationTesting.tests

# Run a specific test file
python manage.py test Testing.Stage7_IntegrationTesting.tests.test_loan_application_workflow

# Run a specific test case
python manage.py test Testing.Stage7_IntegrationTesting.tests.test_loan_application_workflow.LoanApplicationWorkflowTest

# Run a specific test method
python manage.py test Testing.Stage7_IntegrationTesting.tests.test_loan_application_workflow.LoanApplicationWorkflowTest.test_complete_loan_application_workflow
```

## Test Structure

Each test file focuses on a specific integration scenario:

1. `test_loan_application_workflow.py` - Tests the complete loan application process
2. `test_document_workflow_integration.py` - Tests document management workflows
3. `test_calculator_integration.py` - Tests calculator component integration

## API Relationship Validation

These integration tests validate the relationships between different API components as documented in the API Relationship Validation Matrix. The tests specifically verify:

1. **Model Relationships**: Foreign keys, many-to-many fields, and other database relationships
2. **API Endpoint Interactions**: How different endpoints work together in complete workflows
3. **Data Flow**: How data flows between different components of the system
4. **Side Effects**: Notifications, status updates, and other side effects of API operations

## Key Relationships Tested

| Source Component | Target Component | Relationship Type | Validation Method |
|------------------|------------------|-------------------|-------------------|
| Applications | Borrowers | Uses | Foreign key verification |
| Applications | Products | Uses | Foreign key verification |
| Applications | Documents | Links to | Bidirectional relationship testing |
| Documents | Approvals | Triggers | Workflow testing |
| Documents | Signatures | Triggers | Workflow testing |
| Calculator | Fees | Uses | Fee calculation verification |
| Calculator | Products | Uses | Product parameter verification |
| Calculator | Repayments | Outputs to | Repayment schedule verification |
| Notifications | Documents | Triggered by | Notification creation verification |
| Notifications | Approvals | Triggered by | Notification creation verification |

## Test Data

The tests create their own test data including:

- Users with different roles (staff, borrower, approver, signer)
- Borrowers and applications
- Products with different parameters
- Fees of different types
- Documents and related entities

This ensures that tests are self-contained and don't depend on existing database state.
