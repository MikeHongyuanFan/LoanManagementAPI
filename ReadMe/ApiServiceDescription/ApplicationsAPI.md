# Applications API Service

## Overview

The Applications API service is the core component of the Loan Management System, responsible for managing loan applications throughout their lifecycle. It handles application creation, status transitions, stage management, and relationships with other entities such as borrowers, brokers, and products.

## Service Functions

### Primary Functions

1. **Application Management**
   - Create new loan applications
   - Retrieve application details
   - Update application information
   - Delete applications (soft delete)
   - Duplicate existing applications

2. **Status and Stage Management**
   - Transition applications through various statuses (draft, submitted, under_review, approved, rejected, funded, closed)
   - Manage application stages (application, verification, assessment, approval, funding, repayment)
   - Validate status and stage transitions based on business rules

3. **Supporting Entity Management**
   - Associate applications with valuers, quantity surveyors, and referrals
   - Manage business development manager (BDM) assignments

4. **Fee and Repayment Management**
   - Track application fees
   - Manage repayment schedules
   - Handle loan extensions

## Data Flow

### Input Data

- **Borrower Information**: Personal and financial details of the borrower
- **Broker Information** (optional): Details of the broker facilitating the application
- **Product Selection**: The loan product being applied for
- **Loan Details**: Amount, term, purpose, etc.
- **Supporting Entity Assignments**: Valuers, QS, referrals, BDM

### Output Data

- **Application Status**: Current status and stage of the application
- **Application Details**: Complete application information
- **Related Entities**: Links to borrowers, brokers, products, etc.
- **Financial Information**: Loan amounts, fees, repayment schedules

### Internal Processing

1. **Validation Layer**:
   - Validates input data against business rules
   - Ensures required relationships are established
   - Validates status and stage transitions

2. **Business Logic Layer**:
   - Processes application creation and updates
   - Manages status and stage transitions
   - Handles fee calculations and assignments

3. **Data Access Layer**:
   - Interacts with the database models
   - Manages relationships between entities
   - Handles query optimization

## Integration Communication

### Inbound Integrations

1. **User Interface**:
   - Receives application creation and update requests
   - Handles status and stage transition requests

2. **Authentication Service**:
   - Receives user authentication and authorization information
   - Validates user permissions for application actions

### Outbound Integrations

1. **Borrowers API**:
   - Retrieves borrower information
   - Validates borrower existence and eligibility

2. **Brokers API**:
   - Retrieves broker information
   - Validates broker credentials and eligibility

3. **Products API**:
   - Retrieves product information
   - Validates product availability and eligibility

4. **Calculator API**:
   - Requests loan calculations
   - Receives repayment schedules and fee calculations

5. **Document Management API**:
   - Requests document creation and association
   - Receives document status updates

6. **Notifications API**:
   - Sends notification triggers for status changes
   - Receives notification delivery confirmations

## API Reference

### Endpoints

#### Application Management

```
GET /api/applications/
```
- **Description**: List all applications with optional filtering
- **Query Parameters**:
  - `status`: Filter by application status
  - `stage`: Filter by application stage
  - `borrower`: Filter by borrower ID
  - `broker`: Filter by broker ID
  - `product`: Filter by product ID
  - `created_after`: Filter by creation date
  - `created_before`: Filter by creation date
- **Response**: List of application objects with pagination

```
POST /api/applications/
```
- **Description**: Create a new application
- **Request Body**:
  - `borrower_id`: ID of the borrower (required)
  - `broker_id`: ID of the broker (optional)
  - `product_id`: ID of the product (required)
  - `gross_loan_amount`: Gross loan amount (required)
  - `net_loan_amount`: Net loan amount (required)
  - `valuer_id`: ID of the valuer (optional)
  - `qs_id`: ID of the quantity surveyor (optional)
  - `referral_id`: ID of the referral (optional)
  - `bdm_id`: ID of the business development manager (optional)
- **Response**: Created application object

```
GET /api/applications/{id}/
```
- **Description**: Retrieve a specific application
- **Path Parameters**:
  - `id`: Application ID
- **Response**: Application object with related entities

```
PUT /api/applications/{id}/
```
- **Description**: Update an application
- **Path Parameters**:
  - `id`: Application ID
- **Request Body**: Application fields to update
- **Response**: Updated application object

```
DELETE /api/applications/{id}/
```
- **Description**: Delete an application (soft delete)
- **Path Parameters**:
  - `id`: Application ID
- **Response**: Success message

```
POST /api/applications/{id}/duplicate/
```
- **Description**: Duplicate an existing application
- **Path Parameters**:
  - `id`: Application ID to duplicate
- **Response**: New application object

#### Status and Stage Management

```
POST /api/applications/{id}/transition/
```
- **Description**: Transition an application to a new status or stage
- **Path Parameters**:
  - `id`: Application ID
- **Request Body**:
  - `status`: New status (optional)
  - `stage`: New stage (optional)
  - `notes`: Transition notes (optional)
- **Response**: Updated application object

#### Supporting Entity Management

```
GET /api/valuers/
```
- **Description**: List all valuers
- **Response**: List of valuer objects

```
GET /api/valuers/{id}/
```
- **Description**: Retrieve a specific valuer
- **Path Parameters**:
  - `id`: Valuer ID
- **Response**: Valuer object

```
GET /api/qs/
```
- **Description**: List all quantity surveyors
- **Response**: List of QS objects

```
GET /api/qs/{id}/
```
- **Description**: Retrieve a specific quantity surveyor
- **Path Parameters**:
  - `id`: QS ID
- **Response**: QS object

```
GET /api/referrals/
```
- **Description**: List all referrals
- **Response**: List of referral objects

```
GET /api/referrals/{id}/
```
- **Description**: Retrieve a specific referral
- **Path Parameters**:
  - `id`: Referral ID
- **Response**: Referral object

#### Fee and Repayment Management

```
GET /api/fees/
```
- **Description**: List all fees
- **Query Parameters**:
  - `application`: Filter by application ID
- **Response**: List of fee objects

```
GET /api/fees/{id}/
```
- **Description**: Retrieve a specific fee
- **Path Parameters**:
  - `id`: Fee ID
- **Response**: Fee object

```
GET /api/repayments/
```
- **Description**: List all repayments
- **Query Parameters**:
  - `application`: Filter by application ID
- **Response**: List of repayment objects

```
GET /api/repayments/{id}/
```
- **Description**: Retrieve a specific repayment
- **Path Parameters**:
  - `id`: Repayment ID
- **Response**: Repayment object

```
GET /api/loan-extensions/
```
- **Description**: List all loan extensions
- **Query Parameters**:
  - `application`: Filter by application ID
- **Response**: List of loan extension objects

```
GET /api/loan-extensions/{id}/
```
- **Description**: Retrieve a specific loan extension
- **Path Parameters**:
  - `id`: Loan extension ID
- **Response**: Loan extension object

### Data Models

#### Application Model

```json
{
  "id": 1,
  "borrower": {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone_number": "1234567890"
  },
  "broker": {
    "id": 1,
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane.smith@example.com",
    "company_name": "ABC Brokers"
  },
  "product": {
    "id": 1,
    "name": "Standard Loan",
    "interest_rate": 5.5,
    "term_months": 360
  },
  "valuer": {
    "id": 1,
    "name": "Valuation Experts Ltd",
    "contact_info": "contact@valuationexperts.com"
  },
  "qs": null,
  "referral": null,
  "bdm": {
    "id": 1,
    "username": "manager1",
    "email": "manager1@example.com"
  },
  "status": "under_review",
  "stage": "verification",
  "gross_loan_amount": "300000.00",
  "net_loan_amount": "297000.00",
  "created_at": "2023-06-15T10:30:00Z",
  "updated_at": "2023-06-16T14:45:00Z",
  "fees": [
    {
      "id": 1,
      "name": "Application Fee",
      "amount": "500.00",
      "status": "paid"
    }
  ],
  "documents": [
    {
      "id": 1,
      "title": "Loan Agreement",
      "document_type": "agreement",
      "status": "approved"
    }
  ]
}
```

#### Valuer Model

```json
{
  "id": 1,
  "name": "Valuation Experts Ltd",
  "contact_info": "contact@valuationexperts.com",
  "created_at": "2023-01-15T10:30:00Z",
  "updated_at": "2023-01-15T10:30:00Z"
}
```

#### QS Model

```json
{
  "id": 1,
  "name": "Quality Surveyors Inc",
  "contact_info": "contact@qualitysurveyors.com",
  "created_at": "2023-01-15T10:30:00Z",
  "updated_at": "2023-01-15T10:30:00Z"
}
```

#### Referral Model

```json
{
  "id": 1,
  "name": "Partner Agency",
  "source": "Marketing Campaign",
  "created_at": "2023-01-15T10:30:00Z",
  "updated_at": "2023-01-15T10:30:00Z"
}
```

#### Fee Model

```json
{
  "id": 1,
  "application": 1,
  "name": "Application Fee",
  "amount": "500.00",
  "status": "paid",
  "invoice_path": "/media/invoices/app_fee_1.pdf",
  "created_at": "2023-06-15T10:35:00Z",
  "updated_at": "2023-06-15T14:20:00Z"
}
```

#### Repayment Model

```json
{
  "id": 1,
  "application": 1,
  "due_date": "2023-07-15",
  "amount": "1500.00",
  "status": "scheduled",
  "created_at": "2023-06-15T10:35:00Z",
  "updated_at": "2023-06-15T10:35:00Z"
}
```

## Error Handling

The Applications API uses standard HTTP status codes and provides detailed error messages:

- **400 Bad Request**: Invalid input data
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **409 Conflict**: Business rule violation (e.g., invalid status transition)
- **500 Internal Server Error**: Server-side error

Error responses include:
- Error code
- Error message
- Detailed description (when applicable)
- Field-specific errors (for validation errors)

## Security

- **Authentication**: JWT-based authentication required for all endpoints
- **Authorization**: Role-based access control for different operations
- **Data Validation**: Input validation to prevent injection attacks
- **Audit Logging**: All changes to applications are logged with user information

## Performance Considerations

- **Database Optimization**: Indexes on frequently queried fields (status, stage, borrower_id, broker_id)
- **Query Optimization**: Use of select_related and prefetch_related for related entities
- **Pagination**: All list endpoints support pagination to handle large datasets
- **Caching**: Caching of frequently accessed, rarely changing data

## Implementation Notes

- The Applications API is implemented using Django and Django REST Framework
- Database models use PostgreSQL for production and SQLite for development
- API endpoints follow RESTful design principles
- Serializers handle data validation and transformation
- Permissions are enforced at the view level
