# Borrowers API Service

## Overview

The Borrowers API service manages borrower information within the Loan Management System. It handles the creation, retrieval, updating, and deletion of borrower profiles, as well as the association of borrowers with loan applications.

## Service Functions

### Primary Functions

1. **Borrower Profile Management**
   - Create new borrower profiles
   - Retrieve borrower details
   - Update borrower information
   - Delete borrower profiles (soft delete)

2. **Borrower Search and Filtering**
   - Search borrowers by name, email, or other criteria
   - Filter borrowers by various attributes

3. **Application Association**
   - Retrieve applications associated with a borrower
   - Manage borrower-application relationships

## Data Flow

### Input Data

- **Personal Information**: Name, date of birth, contact details
- **Address Information**: Current and previous addresses
- **Contact Preferences**: Preferred contact methods and times
- **Financial Information**: Income, employment details, credit score (optional)

### Output Data

- **Borrower Profile**: Complete borrower information
- **Application Associations**: Links to associated loan applications
- **Document Associations**: Links to borrower documents

### Internal Processing

1. **Validation Layer**:
   - Validates input data against business rules
   - Ensures required fields are provided
   - Validates contact information format

2. **Business Logic Layer**:
   - Processes borrower creation and updates
   - Manages borrower-application relationships
   - Handles borrower search and filtering

3. **Data Access Layer**:
   - Interacts with the database models
   - Manages relationships between entities
   - Handles query optimization

## Integration Communication

### Inbound Integrations

1. **User Interface**:
   - Receives borrower creation and update requests
   - Handles borrower search and filtering requests

2. **Authentication Service**:
   - Receives user authentication and authorization information
   - Validates user permissions for borrower actions

### Outbound Integrations

1. **Applications API**:
   - Provides borrower information for applications
   - Receives application association requests

2. **Document Management API**:
   - Requests document association with borrowers
   - Receives document status updates

3. **Notifications API**:
   - Sends notification triggers for borrower updates
   - Receives notification delivery confirmations

## API Reference

### Endpoints

#### Borrower Management

```
GET /api/borrowers/
```
- **Description**: List all borrowers with optional filtering
- **Query Parameters**:
  - `search`: Search by name or email
  - `state`: Filter by state/province
  - `created_after`: Filter by creation date
  - `created_before`: Filter by creation date
- **Response**: List of borrower objects with pagination

```
POST /api/borrowers/
```
- **Description**: Create a new borrower
- **Request Body**:
  - `first_name`: First name (required)
  - `last_name`: Last name (required)
  - `email`: Email address (required)
  - `phone_number`: Phone number (required)
  - `dob`: Date of birth (required)
  - `address`: Address (optional)
  - `city`: City (optional)
  - `state`: State/Province (optional)
  - `postal_code`: Postal/ZIP code (optional)
  - `country`: Country (optional)
  - `employment_status`: Employment status (optional)
  - `employer`: Employer name (optional)
  - `annual_income`: Annual income (optional)
- **Response**: Created borrower object

```
GET /api/borrowers/{id}/
```
- **Description**: Retrieve a specific borrower
- **Path Parameters**:
  - `id`: Borrower ID
- **Response**: Borrower object with related entities

```
PUT /api/borrowers/{id}/
```
- **Description**: Update a borrower
- **Path Parameters**:
  - `id`: Borrower ID
- **Request Body**: Borrower fields to update
- **Response**: Updated borrower object

```
DELETE /api/borrowers/{id}/
```
- **Description**: Delete a borrower (soft delete)
- **Path Parameters**:
  - `id`: Borrower ID
- **Response**: Success message

#### Application Association

```
GET /api/borrowers/{id}/applications/
```
- **Description**: List all applications for a specific borrower
- **Path Parameters**:
  - `id`: Borrower ID
- **Response**: List of application objects with pagination

### Data Models

#### Borrower Model

```json
{
  "id": 1,
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "phone_number": "1234567890",
  "dob": "1980-01-01",
  "address": "123 Main St",
  "city": "Anytown",
  "state": "CA",
  "postal_code": "12345",
  "country": "USA",
  "employment_status": "Employed",
  "employer": "ABC Company",
  "annual_income": "75000.00",
  "created_at": "2023-06-01T10:30:00Z",
  "updated_at": "2023-06-10T14:45:00Z",
  "applications": [
    {
      "id": 1,
      "status": "under_review",
      "stage": "verification",
      "gross_loan_amount": "300000.00",
      "created_at": "2023-06-15T10:30:00Z"
    }
  ]
}
```

## Error Handling

The Borrowers API uses standard HTTP status codes and provides detailed error messages:

- **400 Bad Request**: Invalid input data
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
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
- **Audit Logging**: All changes to borrower profiles are logged with user information
- **PII Protection**: Personal Identifiable Information is encrypted at rest

## Performance Considerations

- **Database Optimization**: Indexes on frequently queried fields (email, last_name, state)
- **Query Optimization**: Use of select_related and prefetch_related for related entities
- **Pagination**: All list endpoints support pagination to handle large datasets
- **Caching**: Caching of frequently accessed, rarely changing data

## Implementation Notes

- The Borrowers API is implemented using Django and Django REST Framework
- Database models use PostgreSQL for production and SQLite for development
- API endpoints follow RESTful design principles
- Serializers handle data validation and transformation
- Permissions are enforced at the view level
