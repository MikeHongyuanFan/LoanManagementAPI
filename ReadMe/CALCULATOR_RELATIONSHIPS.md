# Calculator Component Relationships

This document outlines the relationships between calculator components in the Loan Management System, including both direct model relationships and business logic connections.

## Model Relationships

### Direct Model Relationships

The calculator module includes the following direct model relationships:

1. **LoanCalculation → Application**
   - One-to-one relationship: Each loan calculation is associated with exactly one application
   - Relationship field: `application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='calculation')`
   - This allows easy access to calculation data from an application: `application.calculation`

2. **LoanCalculation → Product**
   - Many-to-one relationship: Each loan calculation is associated with one product
   - Relationship field: `product = models.ForeignKey(Product, on_delete=models.SET_NULL, related_name='calculations', null=True)`
   - This allows tracking which product was used for the calculation
   - The relationship is nullable to handle cases where the product is deleted

3. **RepaymentSchedule → LoanCalculation**
   - Many-to-one relationship: Each repayment schedule entry belongs to one loan calculation
   - Relationship field: `calculation = models.ForeignKey(LoanCalculation, on_delete=models.CASCADE, related_name='repayments')`
   - This allows easy access to all repayment entries from a calculation: `calculation.repayments.all()`

4. **Fee → Product**
   - Many-to-many relationship: Each fee can be associated with multiple products
   - Relationship field: `products = models.ManyToManyField(Product, related_name='calculator_fees', blank=True)`
   - This allows products to have multiple fees and fees to be shared across products

5. **ApplicationFee → Application**
   - Many-to-one relationship: Each application fee is associated with one application
   - Relationship field: `application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='calculator_fees')`
   - This allows easy access to all fees for an application: `application.calculator_fees.all()`

6. **ApplicationFee → Fee**
   - Many-to-one relationship: Each application fee is an instance of a fee type
   - Relationship field: `fee = models.ForeignKey(Fee, on_delete=models.CASCADE, related_name='application_fees')`
   - This allows tracking which fee definition was used for the application fee

7. **ApplicationFee → LoanCalculation**
   - Many-to-one relationship: Each application fee is associated with one loan calculation
   - Relationship field: `calculation = models.ForeignKey(LoanCalculation, on_delete=models.SET_NULL, related_name='fees', null=True)`
   - This allows tracking which calculation resulted in the fee
   - The relationship is nullable to handle cases where the calculation is deleted

## Business Logic Connections

Beyond direct model relationships, there are several important business logic connections between calculator components:

### 1. Calculation Flow

The calculation flow connects various components in the following sequence:

```
User Input → LoanCalculation → RepaymentSchedule → ApplicationFee → Total Cost
```

1. **User Input**: The user provides loan parameters (amount, term, interest rate)
2. **LoanCalculation**: The system calculates monthly payment and total interest
3. **RepaymentSchedule**: The system generates a detailed repayment schedule
4. **ApplicationFee**: The system calculates applicable fees based on the product
5. **Total Cost**: The system combines all costs to determine the total cost of the loan

### 2. Product-Based Calculations

Products define the parameters used for calculations:

```
Product → Interest Rate → LoanCalculation
Product → Fees → ApplicationFee
```

1. The product's interest rate is used to calculate the loan payment schedule
2. The product's associated fees are used to calculate additional costs

### 3. Application Integration

The calculator integrates with the application workflow:

```
Application → Product Selection → LoanCalculation → Application Status Update
```

1. When an application selects a product, it triggers a loan calculation
2. The loan calculation results may influence the application's status or approval process

## API Integration Points

The calculator components integrate with other system components through these API endpoints:

1. **Calculation API**: `/api/calculator/calculate/`
   - Creates a loan calculation for an application
   - Generates repayment schedule
   - Calculates applicable fees

2. **Product Comparison API**: `/api/calculator/compare-products/`
   - Compares multiple products for the same loan amount
   - Shows differences in payments, interest, and fees

3. **Affordability API**: `/api/calculator/affordability/`
   - Calculates maximum affordable loan amount based on income and expenses
   - Integrates with application pre-qualification process

4. **Fee Management API**: `/api/calculator/fees/`
   - Manages fee definitions
   - Associates fees with products

5. **Application Fee API**: `/api/calculator/application-fees/`
   - Manages fees for specific applications
   - Provides fee waiver functionality

## Data Flow Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│             │     │             │     │             │
│ Application ├────►│   Product   ├────►│     Fee     │
│             │     │             │     │             │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│             │     │             │     │             │
│    Loan     ├────►│  Repayment  │     │Application  │
│ Calculation │     │  Schedule   │     │    Fee      │
│             │     │             │     │             │
└──────┬──────┘     └─────────────┘     └─────────────┘
       │
       │
       ▼
┌─────────────┐
│             │
│  Total Cost │
│ Calculation │
│             │
└─────────────┘
```

## Conclusion

The calculator components are interconnected through both direct model relationships and business logic connections. The direct model relationships provide a solid foundation for data integrity and easy access to related information, while the business logic connections ensure that the calculator functions correctly within the broader loan management system.

By understanding these relationships, developers can more effectively maintain and extend the calculator functionality, ensuring that changes to one component properly propagate to related components.
