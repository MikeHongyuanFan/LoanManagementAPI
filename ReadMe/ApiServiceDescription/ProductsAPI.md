# Products API Service

## Overview

The Products API service manages loan product information within the Loan Management System. It handles the creation, retrieval, updating, and deletion of loan products, as well as the association of products with loan applications and fee structures.

## Service Functions

### Primary Functions

1. **Product Management**
   - Create new loan products
   - Retrieve product details
   - Update product information
   - Delete products (soft delete)

2. **Product Search and Filtering**
   - Search products by name or description
   - Filter products by interest rate, term, or other criteria

3. **Fee Structure Management**
   - Define fees associated with products
   - Manage fee calculation methods
   - Associate fees with products

4. **Eligibility Criteria Management**
   - Define eligibility criteria for products
   - Validate applicant eligibility for products

## Data Flow

### Input Data

- **Product Information**: Name, description, interest rate, term
- **Loan Parameters**: Minimum and maximum loan amounts
- **Fee Structure**: Associated fees and calculation methods
- **Eligibility Criteria**: Requirements for product eligibility

### Output Data

- **Product Details**: Complete product information
- **Fee Structure**: Associated fees and calculation details
- **Application Associations**: Links to applications using the product

### Internal Processing

1. **Validation Layer**:
   - Validates input data against business rules
   - Ensures required fields are provided
   - Validates interest rates and terms

2. **Business Logic Layer**:
   - Processes product creation and updates
   - Manages product-fee relationships
   - Handles product search and filtering

3. **Data Access Layer**:
   - Interacts with the database models
   - Manages relationships between entities
   - Handles query optimization

## Integration Communication

### Inbound Integrations

1. **User Interface**:
   - Receives product creation and update requests
   - Handles product search and filtering requests

2. **Authentication Service**:
   - Receives user authentication and authorization information
   - Validates user permissions for product actions

### Outbound Integrations

1. **Applications API**:
   - Provides product information for applications
   - Receives product selection for applications

2. **Calculator API**:
   - Provides product parameters for loan calculations
   - Receives calculation results based on product terms

3. **Notifications API**:
   - Sends notification triggers for product updates
   - Receives notification delivery confirmations

## API Reference

### Endpoints

#### Product Management

```
GET /api/products/
```
- **Description**: List all products with optional filtering
- **Query Parameters**:
  - `search`: Search by name or description
  - `min_interest_rate`: Filter by minimum interest rate
  - `max_interest_rate`: Filter by maximum interest rate
  - `min_term`: Filter by minimum term in months
  - `max_term`: Filter by maximum term in months
  - `is_active`: Filter by active status
- **Response**: List of product objects with pagination

```
POST /api/products/
```
- **Description**: Create a new product
- **Request Body**:
  - `name`: Product name (required)
  - `description`: Product description (optional)
  - `interest_rate`: Interest rate percentage (required)
  - `term_months`: Term in months (required)
  - `min_loan_amount`: Minimum loan amount (required)
  - `max_loan_amount`: Maximum loan amount (required)
  - `is_active`: Whether the product is active (default: true)
  - `eligibility_criteria`: JSON object with eligibility criteria (optional)
- **Response**: Created product object

```
GET /api/products/{id}/
```
- **Description**: Retrieve a specific product
- **Path Parameters**:
  - `id`: Product ID
- **Response**: Product object with related entities

```
PUT /api/products/{id}/
```
- **Description**: Update a product
- **Path Parameters**:
  - `id`: Product ID
- **Request Body**: Product fields to update
- **Response**: Updated product object

```
DELETE /api/products/{id}/
```
- **Description**: Delete a product (soft delete)
- **Path Parameters**:
  - `id`: Product ID
- **Response**: Success message

#### Fee Structure Management

```
GET /api/products/{product_id}/fees/
```
- **Description**: List all fees for a specific product
- **Path Parameters**:
  - `product_id`: Product ID
- **Response**: List of fee objects

```
POST /api/products/{product_id}/fees/
```
- **Description**: Associate a fee with a product
- **Path Parameters**:
  - `product_id`: Product ID
- **Request Body**:
  - `fee_id`: Fee ID (required)
  - `is_required`: Whether the fee is required (default: true)
  - `override_amount`: Override the default fee amount (optional)
- **Response**: Created product-fee association

```
GET /api/products/{product_id}/fees/{id}/
```
- **Description**: Retrieve a specific fee for a product
- **Path Parameters**:
  - `product_id`: Product ID
  - `id`: Fee ID
- **Response**: Fee object

```
DELETE /api/products/{product_id}/fees/{id}/
```
- **Description**: Remove a fee association from a product
- **Path Parameters**:
  - `product_id`: Product ID
  - `id`: Fee ID
- **Response**: Success message

### Data Models

#### Product Model

```json
{
  "id": 1,
  "name": "Standard Loan",
  "description": "Standard loan product with competitive interest rates",
  "interest_rate": 5.5,
  "term_months": 360,
  "min_loan_amount": 10000.00,
  "max_loan_amount": 500000.00,
  "is_active": true,
  "eligibility_criteria": {
    "min_credit_score": 650,
    "min_income": 50000,
    "max_debt_to_income": 0.43
  },
  "created_at": "2023-01-15T10:30:00Z",
  "updated_at": "2023-05-20T14:45:00Z",
  "fees": [
    {
      "id": 1,
      "name": "Application Fee",
      "amount": 500.00,
      "fee_type": "application",
      "calculation_method": "fixed"
    },
    {
      "id": 2,
      "name": "Establishment Fee",
      "amount": 1.0,
      "fee_type": "establishment",
      "calculation_method": "percentage"
    }
  ],
  "application_count": 24
}
```

#### Product-Fee Association Model

```json
{
  "id": 1,
  "product": 1,
  "fee": {
    "id": 1,
    "name": "Application Fee",
    "amount": 500.00,
    "fee_type": "application",
    "calculation_method": "fixed"
  },
  "is_required": true,
  "override_amount": null,
  "created_at": "2023-01-15T10:35:00Z",
  "updated_at": "2023-01-15T10:35:00Z"
}
```

## Error Handling

The Products API uses standard HTTP status codes and provides detailed error messages:

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
- **Audit Logging**: All changes to products are logged with user information

## Performance Considerations

- **Database Optimization**: Indexes on frequently queried fields (name, interest_rate, term_months)
- **Query Optimization**: Use of select_related and prefetch_related for related entities
- **Pagination**: All list endpoints support pagination to handle large datasets
- **Caching**: Caching of frequently accessed, rarely changing product data

## Implementation Notes

- The Products API is implemented using Django and Django REST Framework
- Database models use PostgreSQL for production and SQLite for development
- API endpoints follow RESTful design principles
- Serializers handle data validation and transformation
- Permissions are enforced at the view level
