# API Service Documentation

This directory contains detailed documentation for each API service in the CRM Loan Management System. Each document provides comprehensive information about the service's functions, data flow, integration communication, API reference, and implementation details.

## Available API Services

1. [Applications API](ApplicationsAPI.md) - Core service for managing loan applications throughout their lifecycle
2. [Borrowers API](BorrowersAPI.md) - Service for managing borrower profiles and their relationships with applications
3. [Brokers API](BrokersAPI.md) - Service for managing broker profiles and their relationships with applications
4. [Products API](ProductsAPI.md) - Service for managing loan products, their parameters, and fee structures
5. [Document Management API](DocumentManagementAPI.md) - Comprehensive service for document handling, workflows, and organization
6. [Calculator API](CalculatorAPI.md) - Service for loan calculations, amortization schedules, and fee calculations
7. [Notifications API](NotificationsAPI.md) - Service for system notifications, email notifications, and notes
8. [Dashboard API](DashboardAPI.md) - Service for data aggregation, visualization, and reporting

## Documentation Structure

Each API service documentation follows a consistent structure:

1. **Overview** - Brief description of the service and its purpose
2. **Service Functions** - Detailed explanation of the primary functions provided by the service
3. **Data Flow** - Description of input data, output data, and internal processing
4. **Integration Communication** - Documentation of inbound and outbound integrations with other services
5. **API Reference** - Comprehensive list of endpoints with request/response details
6. **Data Models** - JSON representations of the key data models used by the service
7. **Error Handling** - Description of error handling mechanisms and error response formats
8. **Security** - Security considerations and implementation details
9. **Performance Considerations** - Optimization strategies and performance considerations
10. **Implementation Notes** - Technical details about the implementation

## API Relationships

For a comprehensive analysis of the relationships between API services and their data flows, refer to the [API Relationship Data Flow Analysis](../API_Relationship_Data_Flow_Analysis.md) document.

## Integration Testing

For information about the integration test coverage and identified gaps, refer to the [API Integration Testing Gap Analysis](../API_Integration_Testing_Gap_Analysis.md) document.

## Implementation Status

The implementation status of each API service is tracked in the project's main [README.md](../../README.md) under the "Development Status" section. Currently:

- ✅ **Phase 1: Core Features** (Completed)
  - User authentication and authorization
  - Borrower management
  - Loan application processing
  - Loan product configuration
  - Basic document management
  - Notification system

- ✅ **Phase 2: Advanced Document Management** (Completed)
  - Document versioning with comparison and rollback
  - Enhanced approval workflow with multi-step processes
  - Notification system integration
  - Electronic signature integration
  - Full-text search for document content
  - Advanced document organization features

- 🔄 **Phase 3: Loan Servicing** (Planned)
  - Payment tracking and processing (manual implementation)
  - Late payment management
  - Interest calculation
  - Payment reminders and notifications
  - Payment history and reporting

- 🔄 **Phase 4: Reporting and Analytics** (Planned)
  - Dashboard with key metrics
  - Custom report generation
  - Data visualization
  - Export functionality
  - Scheduled reports

- 🔄 **Phase 5: Integrations** (Planned)
  - Document OCR and data extraction
  - Optional third-party integrations
