# Dashboard Module

## Overview

The Dashboard module provides a comprehensive set of APIs for monitoring and visualizing key metrics related to loan applications, documents, borrowers, and brokers. It includes features for data aggregation, caching, and customizable dashboard layouts.

## Features

- **Aggregated Metrics**: Collects and processes data from various parts of the system
- **Real-time Updates**: Metrics are updated in real-time as data changes
- **Customizable Dashboards**: Users can create and customize their own dashboard layouts
- **Performance Optimized**: Includes caching and query optimization for fast response times
- **API-First Design**: All functionality is available through RESTful APIs

## Architecture

The Dashboard module is built with the following components:

1. **Models**:
   - `DashboardMetric`: Stores individual metrics with values and metadata
   - `DashboardWidget`: Represents visualization components that display metrics
   - `DashboardLayout`: Defines the arrangement of widgets on a dashboard
   - `DashboardWidgetPlacement`: Maps widgets to specific positions within a layout
   - `UserDashboardPreference`: Stores user-specific dashboard settings

2. **Services**:
   - `MetricAggregationService`: Collects and processes data from various sources
   - Caching utilities for optimizing performance

3. **APIs**:
   - Overview API: Provides a high-level summary of all metrics
   - Application Dashboard API: Focuses on loan application metrics
   - Document Dashboard API: Focuses on document metrics
   - Entity Dashboard API: Focuses on borrower and broker metrics
   - Widget and Layout APIs: For managing dashboard customization

## API Reference

### Overview API

```
GET /api/dashboard/overview/
```

Returns a comprehensive overview of all key metrics in the system.

**Query Parameters**:
- `days` (optional): Number of days to include in time-series data (default: 30)

**Response Example**:
```json
{
  "loan_applications": {
    "total_applications": 250,
    "applications_by_status": {
      "pending": 45,
      "approved": 180,
      "rejected": 25
    },
    "total_loan_amount": 12500000
  },
  "documents": {
    "total_documents": 750,
    "documents_by_type": {
      "application": 250,
      "contract": 200,
      "identity": 300
    },
    "documents_pending_approval": 30
  },
  "borrowers": {
    "total_borrowers": 200,
    "borrowers_by_state": {
      "CA": 75,
      "NY": 45,
      "TX": 35,
      "FL": 25,
      "other": 20
    }
  },
  "brokers": {
    "total_brokers": 50
  },
  "products": {
    "total_products": 15,
    "products_by_usage": {
      "Standard Loan": 120,
      "Premium Loan": 80,
      "Quick Loan": 50
    }
  },
  "last_updated": "2025-04-13T08:25:24Z"
}
```

### Application Dashboard API

```
GET /api/dashboard/applications/
```

Returns detailed metrics about loan applications.

**Query Parameters**:
- `days` (optional): Number of days to include in time-series data (default: 30)

**Response Example**:
```json
{
  "applications_over_time": [
    {"date": "2025-04-01", "count": 12},
    {"date": "2025-04-02", "count": 15},
    {"date": "2025-04-03", "count": 10}
  ],
  "applications_by_status": [
    {"status": "approved", "count": 180},
    {"status": "pending", "count": 45},
    {"status": "rejected", "count": 25}
  ],
  "applications_by_product": [
    {"product__name": "Standard Loan", "count": 120},
    {"product__name": "Premium Loan", "count": 80},
    {"product__name": "Quick Loan", "count": 50}
  ],
  "top_brokers": [
    {
      "broker__id": 1,
      "broker__first_name": "John",
      "broker__last_name": "Smith",
      "count": 45
    },
    {
      "broker__id": 2,
      "broker__first_name": "Jane",
      "broker__last_name": "Doe",
      "count": 32
    }
  ],
  "loan_amount_distribution": [
    {"label": "0-100K", "count": 75},
    {"label": "100K-250K", "count": 95},
    {"label": "250K-500K", "count": 60},
    {"label": "500K-1M", "count": 15},
    {"label": "1M+", "count": 5}
  ],
  "last_updated": "2025-04-13T08:25:24Z"
}
```

### Document Dashboard API

```
GET /api/dashboard/documents/
```

Returns detailed metrics about documents.

**Query Parameters**:
- `days` (optional): Number of days to include in time-series data (default: 30)

**Response Example**:
```json
{
  "documents_over_time": [
    {"date": "2025-04-01", "count": 25},
    {"date": "2025-04-02", "count": 30},
    {"date": "2025-04-03", "count": 22}
  ],
  "documents_by_type": [
    {"document_type": "application", "count": 250},
    {"document_type": "contract", "count": 200},
    {"document_type": "identity", "count": 300}
  ],
  "documents_by_status": [
    {"status": "approved", "count": 600},
    {"status": "pending_approval", "count": 30},
    {"status": "rejected", "count": 120}
  ],
  "approval_metrics": {
    "average_approval_time": "2.5 days",
    "approval_rate": 83.3
  },
  "last_updated": "2025-04-13T08:25:24Z"
}
```

### Entity Dashboard API

```
GET /api/dashboard/entities/
```

Returns detailed metrics about borrowers and brokers.

**Query Parameters**:
- `days` (optional): Number of days to include in time-series data (default: 30)

**Response Example**:
```json
{
  "borrowers_over_time": [
    {"date": "2025-04-01", "count": 8},
    {"date": "2025-04-02", "count": 12},
    {"date": "2025-04-03", "count": 7}
  ],
  "borrowers_by_state": [
    {"state": "CA", "count": 75},
    {"state": "NY", "count": 45},
    {"state": "TX", "count": 35},
    {"state": "FL", "count": 25},
    {"state": "other", "count": 20}
  ],
  "brokers_over_time": [
    {"date": "2025-04-01", "count": 2},
    {"date": "2025-04-02", "count": 1},
    {"date": "2025-04-03", "count": 3}
  ],
  "top_borrowers": [
    {
      "borrower__id": 1,
      "borrower__first_name": "Alice",
      "borrower__last_name": "Johnson",
      "total_loan_amount": 750000,
      "application_count": 3
    },
    {
      "borrower__id": 2,
      "borrower__first_name": "Bob",
      "borrower__last_name": "Williams",
      "total_loan_amount": 500000,
      "application_count": 2
    }
  ],
  "top_brokers": [
    {
      "broker__id": 1,
      "broker__first_name": "John",
      "broker__last_name": "Smith",
      "total_loan_amount": 5000000,
      "application_count": 45
    },
    {
      "broker__id": 2,
      "broker__first_name": "Jane",
      "broker__last_name": "Doe",
      "total_loan_amount": 3500000,
      "application_count": 32
    }
  ],
  "last_updated": "2025-04-13T08:25:24Z"
}
```

### Dashboard Widgets API

```
GET /api/dashboard/widgets/
POST /api/dashboard/widgets/
GET /api/dashboard/widgets/{id}/
PUT /api/dashboard/widgets/{id}/
PATCH /api/dashboard/widgets/{id}/
DELETE /api/dashboard/widgets/{id}/
```

Manages dashboard widgets.

**POST Request Example**:
```json
{
  "name": "application_status_chart",
  "display_name": "Application Status Distribution",
  "description": "Pie chart showing the distribution of application statuses",
  "widget_type": "chart_pie",
  "configuration": {
    "title": "Application Status",
    "height": 300,
    "colors": ["#4CAF50", "#FFC107", "#F44336"]
  },
  "position_x": 0,
  "position_y": 0,
  "width": 2,
  "height": 2
}
```

### Dashboard Layouts API

```
GET /api/dashboard/layouts/
POST /api/dashboard/layouts/
GET /api/dashboard/layouts/{id}/
PUT /api/dashboard/layouts/{id}/
PATCH /api/dashboard/layouts/{id}/
DELETE /api/dashboard/layouts/{id}/
```

Manages dashboard layouts.

**POST Request Example**:
```json
{
  "name": "default_layout",
  "description": "Default dashboard layout",
  "is_default": true,
  "widgets": [
    {
      "widget_id": 1,
      "position_x": 0,
      "position_y": 0,
      "width": 2,
      "height": 2
    },
    {
      "widget_id": 2,
      "position_x": 2,
      "position_y": 0,
      "width": 2,
      "height": 1
    }
  ]
}
```

### User Dashboard Preferences API

```
GET /api/dashboard/preferences/
POST /api/dashboard/preferences/
GET /api/dashboard/preferences/{id}/
PUT /api/dashboard/preferences/{id}/
PATCH /api/dashboard/preferences/{id}/
DELETE /api/dashboard/preferences/{id}/
```

Manages user dashboard preferences.

**POST Request Example**:
```json
{
  "layout_id": 1,
  "custom_settings": {
    "theme": "dark",
    "refresh_interval": 60,
    "default_date_range": 30
  }
}
```

## Caching Strategy

The Dashboard module implements a comprehensive caching strategy to optimize performance:

1. **Cache Keys**: Cache keys are generated based on the endpoint and query parameters
2. **Cache Duration**: Default cache duration is 5 minutes (configurable)
3. **Cache Invalidation**: Cache is automatically invalidated when related data changes
4. **Selective Caching**: Only expensive queries are cached

## Performance Considerations

1. **Query Optimization**: Queries are optimized to minimize database load
2. **Aggregation**: Data is pre-aggregated where possible
3. **Pagination**: Large result sets are paginated
4. **Monitoring**: Response times are monitored and logged

## Testing

The Dashboard module includes a comprehensive test suite:

- **Model Tests**: Tests for all dashboard models
- **API Tests**: Tests for all API endpoints
- **Service Tests**: Tests for the metric aggregation service
- **Cache Tests**: Tests for the caching utilities
- **Performance Tests**: Tests for API performance

To run the tests:

```bash
python manage.py test dashboard
```

## Future Enhancements

1. **Real-time Updates**: Implement WebSocket support for real-time dashboard updates
2. **Advanced Visualizations**: Add support for more complex visualization types
3. **Drill-down Capabilities**: Allow users to drill down into specific metrics
4. **Export Functionality**: Add support for exporting dashboard data
5. **Scheduled Reports**: Implement scheduled report generation and delivery
