# Calculator API Service

## Overview

The Calculator API service provides comprehensive loan calculation functionality within the Loan Management System. It handles various types of calculations including amortization schedules, interest-only calculations, fee calculations, and total cost analysis.

## Service Functions

### Primary Functions

1. **Loan Calculations**
   - Calculate monthly payments
   - Generate amortization schedules
   - Calculate interest-only payments
   - Determine total interest and cost of loan

2. **Fee Calculations**
   - Calculate application fees
   - Calculate establishment fees
   - Calculate ongoing fees
   - Determine total fee costs

3. **Product Comparison**
   - Compare different loan products
   - Calculate cost differences between products
   - Determine optimal product based on criteria

4. **Affordability Analysis**
   - Calculate borrowing capacity
   - Determine debt service ratios
   - Analyze repayment affordability

## Data Flow

### Input Data

- **Loan Parameters**: Principal amount, interest rate, term
- **Product Information**: Product-specific parameters and fees
- **Fee Structure**: Fee types, amounts, and calculation methods
- **Borrower Information**: Income, expenses, existing debt (for affordability)

### Output Data

- **Payment Information**: Monthly payment amounts
- **Amortization Schedule**: Detailed repayment schedule
- **Fee Calculations**: Calculated fee amounts
- **Total Cost Analysis**: Total cost of loan including interest and fees

### Internal Processing

1. **Validation Layer**:
   - Validates input parameters
   - Ensures required fields are provided
   - Validates numerical ranges

2. **Calculation Layer**:
   - Performs financial calculations
   - Generates repayment schedules
   - Calculates fees based on rules

3. **Data Access Layer**:
   - Stores calculation results
   - Retrieves product and fee information
   - Manages calculation history

## Integration Communication

### Inbound Integrations

1. **User Interface**:
   - Receives calculation requests
   - Handles product comparison requests

2. **Applications API**:
   - Receives loan application data for calculations
   - Requests calculation results for applications

3. **Products API**:
   - Receives product information for calculations
   - Requests fee structure information

### Outbound Integrations

1. **Applications API**:
   - Provides calculation results for applications
   - Receives application updates

2. **Document Management API**:
   - Requests document generation for calculation results
   - Receives document references

## API Reference

### Endpoints

#### Loan Calculations

```
POST /api/calculator/monthly-payment/
```
- **Description**: Calculate monthly payment for a loan
- **Request Body**:
  - `principal`: Loan principal amount (required)
  - `interest_rate`: Annual interest rate as percentage (required)
  - `term_years`: Loan term in years (required)
  - `interest_only`: Whether calculation is interest-only (default: false)
- **Response**: Monthly payment amount

```
POST /api/calculator/amortization-schedule/
```
- **Description**: Generate amortization schedule for a loan
- **Request Body**:
  - `principal`: Loan principal amount (required)
  - `interest_rate`: Annual interest rate as percentage (required)
  - `term_years`: Loan term in years (required)
  - `start_date`: Start date for the schedule (default: current date)
- **Response**: Amortization schedule with payment details

```
POST /api/calculator/loan-summary/
```
- **Description**: Calculate loan summary including total interest and payments
- **Request Body**:
  - `principal`: Loan principal amount (required)
  - `interest_rate`: Annual interest rate as percentage (required)
  - `term_years`: Loan term in years (required)
  - `fees`: Array of fee objects (optional)
- **Response**: Loan summary with total interest, payments, and fees

#### Fee Calculations

```
GET /api/calculator/fees/
```
- **Description**: List all available fees
- **Query Parameters**:
  - `fee_type`: Filter by fee type
  - `is_active`: Filter by active status
- **Response**: List of fee objects

```
POST /api/calculator/application-fees/
```
- **Description**: Calculate fees for an application
- **Request Body**:
  - `application_id`: Application ID (required)
  - `loan_amount`: Loan amount (required)
  - `product_id`: Product ID (required)
- **Response**: Calculated fee amounts for the application

#### Product Comparison

```
POST /api/calculator/product-payment/
```
- **Description**: Calculate payment for a specific product
- **Request Body**:
  - `product_id`: Product ID (required)
  - `loan_amount`: Loan amount (required)
  - `term_years`: Override product term in years (optional)
- **Response**: Payment details for the product

```
POST /api/calculator/compare-products/
```
- **Description**: Compare multiple products
- **Request Body**:
  - `product_ids`: Array of product IDs (required)
  - `loan_amount`: Loan amount (required)
  - `term_years`: Term in years (optional)
- **Response**: Comparison of products with payment and cost details

#### Affordability Analysis

```
POST /api/calculator/affordability/
```
- **Description**: Calculate borrowing capacity
- **Request Body**:
  - `annual_income`: Annual income (required)
  - `monthly_expenses`: Monthly expenses (required)
  - `existing_debt`: Existing debt payments (required)
  - `interest_rate`: Expected interest rate (required)
  - `term_years`: Expected loan term (required)
- **Response**: Maximum borrowing capacity and affordability metrics

### Stored Calculations

```
GET /api/calculator/calculations/
```
- **Description**: List all stored calculations
- **Query Parameters**:
  - `application`: Filter by application ID
- **Response**: List of calculation objects

```
POST /api/calculator/calculations/
```
- **Description**: Create a new stored calculation
- **Request Body**:
  - `application_id`: Application ID (required)
  - `product_id`: Product ID (required)
  - `interest_type`: Interest type (required)
  - `interest_rate`: Interest rate (required)
  - `loan_amount`: Loan amount (required)
  - `loan_term_years`: Loan term in years (required)
  - `compounding_period`: Compounding period (default: 'monthly')
- **Response**: Created calculation object with results

```
GET /api/calculator/calculations/{id}/
```
- **Description**: Retrieve a specific calculation
- **Path Parameters**:
  - `id`: Calculation ID
- **Response**: Calculation object with results

```
GET /api/calculator/repayments/
```
- **Description**: List all repayment schedules
- **Query Parameters**:
  - `calculation`: Filter by calculation ID
- **Response**: List of repayment schedule objects

```
GET /api/calculator/repayments/{id}/
```
- **Description**: Retrieve a specific repayment schedule entry
- **Path Parameters**:
  - `id`: Repayment schedule entry ID
- **Response**: Repayment schedule entry object

### Data Models

#### LoanCalculation Model

```json
{
  "id": 1,
  "application": {
    "id": 1,
    "borrower": "John Doe",
    "status": "under_review"
  },
  "product": {
    "id": 1,
    "name": "Standard Loan",
    "interest_rate": 5.5
  },
  "interest_type": "fixed",
  "interest_rate": 5.5,
  "loan_amount": 300000.00,
  "loan_term_years": 30,
  "compounding_period": "monthly",
  "monthly_payment": 1703.37,
  "total_payments": 613213.20,
  "total_interest": 313213.20,
  "created_at": "2023-06-15T10:30:00Z",
  "updated_at": "2023-06-15T10:30:00Z",
  "repayments": [
    {
      "id": 1,
      "payment_number": 1,
      "payment_date": "2023-07-15",
      "payment_amount": 1703.37,
      "principal_amount": 378.37,
      "interest_amount": 1325.00,
      "remaining_balance": 299621.63
    },
    {
      "id": 2,
      "payment_number": 2,
      "payment_date": "2023-08-15",
      "payment_amount": 1703.37,
      "principal_amount": 380.04,
      "interest_amount": 1323.33,
      "remaining_balance": 299241.59
    }
  ],
  "fees": [
    {
      "id": 1,
      "fee": {
        "id": 1,
        "name": "Application Fee",
        "fee_type": "application"
      },
      "calculated_amount": 500.00,
      "is_waived": false
    },
    {
      "id": 2,
      "fee": {
        "id": 2,
        "name": "Establishment Fee",
        "fee_type": "establishment"
      },
      "calculated_amount": 3000.00,
      "is_waived": false
    }
  ]
}
```

#### RepaymentSchedule Model

```json
{
  "id": 1,
  "calculation": 1,
  "payment_number": 1,
  "payment_date": "2023-07-15",
  "payment_amount": 1703.37,
  "principal_amount": 378.37,
  "interest_amount": 1325.00,
  "remaining_balance": 299621.63
}
```

#### Fee Model

```json
{
  "id": 1,
  "name": "Application Fee",
  "description": "Fee for processing application",
  "fee_type": "application",
  "calculation_method": "fixed",
  "amount": 500.00,
  "is_active": true,
  "products": [1, 2, 3],
  "created_at": "2023-01-15T10:30:00Z",
  "updated_at": "2023-01-15T10:30:00Z"
}
```

#### ApplicationFee Model

```json
{
  "id": 1,
  "application": 1,
  "fee": 1,
  "calculation": 1,
  "calculated_amount": 500.00,
  "is_waived": false,
  "waiver_reason": null,
  "created_at": "2023-06-15T10:35:00Z",
  "updated_at": "2023-06-15T10:35:00Z"
}
```

## Error Handling

The Calculator API uses standard HTTP status codes and provides detailed error messages:

- **400 Bad Request**: Invalid input data
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Valid request but calculation cannot be performed
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
- **Audit Logging**: All calculations are logged with user information

## Performance Considerations

- **Calculation Optimization**: Efficient algorithms for financial calculations
- **Database Optimization**: Indexes on frequently queried fields
- **Caching**: Caching of calculation results for repeated requests
- **Pagination**: All list endpoints support pagination to handle large datasets

## Implementation Notes

- The Calculator API is implemented using Django and Django REST Framework
- Financial calculations use Python's decimal module for precision
- Complex calculations are performed using specialized financial libraries
- Results are stored in the database for reference and reporting
- API endpoints follow RESTful design principles
