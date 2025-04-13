# Dashboard API Reference

## Overview

The Dashboard module provides a comprehensive set of APIs for monitoring and visualizing key metrics related to loan applications, documents, borrowers, and brokers.

## Base URL

All API endpoints are relative to: `/api/dashboard/`

## Authentication

All endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <token>
```

## Endpoints

### Overview API

```
GET /overview/
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
GET /applications/
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
GET /documents/
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
GET /entities/
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

### Dashboard Metrics API

```
GET /metrics/
GET /metrics/{id}/
```

Retrieves dashboard metrics.

**Query Parameters**:
- `category` (optional): Filter metrics by category (e.g., 'application', 'document', 'borrower', 'broker', 'product')
- `metric_type` (optional): Filter metrics by type (e.g., 'count', 'percentage', 'currency', 'custom')

**Response Example**:
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "total_applications",
      "display_name": "Total Applications",
      "description": "Total number of loan applications",
      "category": "application",
      "metric_type": "count",
      "value": 250,
      "json_value": null,
      "last_updated": "2025-04-13T08:25:24Z"
    },
    {
      "id": 2,
      "name": "applications_by_status",
      "display_name": "Applications by Status",
      "description": "Distribution of applications by status",
      "category": "application",
      "metric_type": "custom",
      "value": null,
      "json_value": {
        "pending": 45,
        "approved": 180,
        "rejected": 25
      },
      "last_updated": "2025-04-13T08:25:24Z"
    }
  ]
}
```

### Dashboard Widgets API

```
GET /widgets/
POST /widgets/
GET /widgets/{id}/
PUT /widgets/{id}/
PATCH /widgets/{id}/
DELETE /widgets/{id}/
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
  "height": 2,
  "metrics": [1, 2]
}
```

**Response Example**:
```json
{
  "id": 1,
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
  "height": 2,
  "metrics": [
    {
      "id": 1,
      "name": "total_applications",
      "display_name": "Total Applications"
    },
    {
      "id": 2,
      "name": "applications_by_status",
      "display_name": "Applications by Status"
    }
  ],
  "created_at": "2025-04-13T08:25:24Z",
  "updated_at": "2025-04-13T08:25:24Z",
  "created_by": 1
}
```

### Dashboard Layouts API

```
GET /layouts/
POST /layouts/
GET /layouts/{id}/
PUT /layouts/{id}/
PATCH /layouts/{id}/
DELETE /layouts/{id}/
```

Manages dashboard layouts.

**POST Request Example**:
```json
{
  "name": "default_layout",
  "description": "Default dashboard layout",
  "is_default": true
}
```

**Response Example**:
```json
{
  "id": 1,
  "name": "default_layout",
  "description": "Default dashboard layout",
  "is_default": true,
  "widgets": [],
  "created_at": "2025-04-13T08:25:24Z",
  "updated_at": "2025-04-13T08:25:24Z",
  "created_by": 1
}
```

### Widget Placement API

```
POST /layouts/{layout_id}/widgets/
DELETE /layouts/{layout_id}/widgets/{widget_id}/
```

Manages widget placement within layouts.

**POST Request Example**:
```json
{
  "widget_id": 1,
  "position_x": 0,
  "position_y": 0,
  "width": 2,
  "height": 2
}
```

**Response Example**:
```json
{
  "id": 1,
  "widget": {
    "id": 1,
    "name": "application_status_chart",
    "display_name": "Application Status Distribution"
  },
  "position_x": 0,
  "position_y": 0,
  "width": 2,
  "height": 2
}
```

### User Dashboard Preferences API

```
GET /preferences/
POST /preferences/
GET /preferences/{id}/
PUT /preferences/{id}/
PATCH /preferences/{id}/
DELETE /preferences/{id}/
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

**Response Example**:
```json
{
  "id": 1,
  "user": 1,
  "layout": {
    "id": 1,
    "name": "default_layout",
    "description": "Default dashboard layout"
  },
  "custom_settings": {
    "theme": "dark",
    "refresh_interval": 60,
    "default_date_range": 30
  }
}
```

## Error Responses

All API endpoints return standard HTTP status codes:

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error responses include a JSON body with details:

```json
{
  "error": "Error message",
  "detail": "Detailed error description"
}
```

## Rate Limiting

API requests are rate-limited to 100 requests per minute per user. Rate limit headers are included in all responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1586956800
```

## Caching

Responses may be cached to improve performance. Cache headers are included in responses:

```
Cache-Control: max-age=300
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"
```

## Performance Monitoring

Performance metrics are included in response headers:

```
X-Dashboard-Response-Time: 0.125s
```
