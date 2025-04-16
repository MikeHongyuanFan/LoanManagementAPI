# Dashboard API Service

## Overview

The Dashboard API service provides data aggregation, visualization, and reporting capabilities for the Loan Management System. It offers customizable dashboards with widgets displaying key metrics, trends, and performance indicators.

## Service Functions

### Primary Functions

1. **Metric Management**
   - Calculate and store key metrics
   - Retrieve metric data
   - Update metrics on schedule
   - Define custom metrics

2. **Widget Management**
   - Create and configure dashboard widgets
   - Retrieve widget data
   - Update widget configurations
   - Position widgets on dashboards

3. **Layout Management**
   - Create dashboard layouts
   - Customize layout configurations
   - Set default layouts
   - Manage layout sharing

4. **User Preferences**
   - Store user dashboard preferences
   - Retrieve user-specific settings
   - Update user preferences
   - Reset to default settings

## Data Flow

### Input Data

- **Raw Data**: Data from various API services
- **Metric Definitions**: Formulas and rules for metric calculation
- **Widget Configurations**: Display settings and data sources
- **Layout Settings**: Widget positioning and sizing
- **User Preferences**: User-specific dashboard settings

### Output Data

- **Calculated Metrics**: Processed metric values
- **Widget Data**: Data formatted for widget display
- **Dashboard Layouts**: Complete dashboard configurations
- **Aggregated Reports**: Summarized data for reporting

### Internal Processing

1. **Data Aggregation Layer**:
   - Collects data from various sources
   - Processes and transforms data
   - Calculates metrics based on formulas
   - Stores results for quick access

2. **Presentation Layer**:
   - Formats data for different widget types
   - Applies user preferences
   - Handles layout positioning
   - Manages widget interactions

3. **Data Access Layer**:
   - Interacts with the database models
   - Manages relationships between entities
   - Handles query optimization

## Integration Communication

### Inbound Integrations

1. **User Interface**:
   - Receives dashboard configuration requests
   - Handles widget interaction events

2. **Authentication Service**:
   - Receives user authentication and authorization information
   - Validates user permissions for dashboard actions

### Outbound Integrations

1. **Applications API**:
   - Retrieves application data for metrics
   - Monitors application status changes

2. **Document Management API**:
   - Retrieves document statistics
   - Monitors document workflow events

3. **Calculator API**:
   - Retrieves calculation data for financial metrics
   - Monitors calculation events

4. **Borrowers/Brokers API**:
   - Retrieves entity data for relationship metrics
   - Monitors entity changes

## API Reference

### Endpoints

#### Metric Management

```
GET /api/dashboard/metrics/
```
- **Description**: List all dashboard metrics
- **Query Parameters**:
  - `category`: Filter by metric category
  - `metric_type`: Filter by metric type
  - `is_active`: Filter by active status
- **Response**: List of metric objects

```
POST /api/dashboard/metrics/
```
- **Description**: Create a new dashboard metric
- **Request Body**:
  - `name`: Metric name (required)
  - `display_name`: Display name (required)
  - `description`: Metric description (optional)
  - `category`: Metric category (required)
  - `metric_type`: Metric type (required)
  - `value`: Decimal value (optional)
  - `string_value`: String value (optional)
  - `json_value`: JSON value (optional)
  - `is_active`: Whether the metric is active (default: true)
- **Response**: Created metric object

```
GET /api/dashboard/metrics/{id}/
```
- **Description**: Retrieve a specific metric
- **Path Parameters**:
  - `id`: Metric ID
- **Response**: Metric object

```
PUT /api/dashboard/metrics/{id}/
```
- **Description**: Update a metric
- **Path Parameters**:
  - `id`: Metric ID
- **Request Body**: Metric fields to update
- **Response**: Updated metric object

```
DELETE /api/dashboard/metrics/{id}/
```
- **Description**: Delete a metric
- **Path Parameters**:
  - `id`: Metric ID
- **Response**: Success message

#### Widget Management

```
GET /api/dashboard/widgets/
```
- **Description**: List all dashboard widgets
- **Query Parameters**:
  - `widget_type`: Filter by widget type
  - `is_active`: Filter by active status
  - `created_by`: Filter by creator user ID
- **Response**: List of widget objects

```
POST /api/dashboard/widgets/
```
- **Description**: Create a new dashboard widget
- **Request Body**:
  - `name`: Widget name (required)
  - `display_name`: Display name (required)
  - `description`: Widget description (optional)
  - `widget_type`: Widget type (required)
  - `metrics`: Array of metric IDs (required)
  - `configuration`: Widget configuration JSON (required)
  - `position_x`: X position (default: 0)
  - `position_y`: Y position (default: 0)
  - `width`: Widget width (default: 1)
  - `height`: Widget height (default: 1)
  - `is_active`: Whether the widget is active (default: true)
- **Response**: Created widget object

```
GET /api/dashboard/widgets/{id}/
```
- **Description**: Retrieve a specific widget
- **Path Parameters**:
  - `id`: Widget ID
- **Response**: Widget object with metrics

```
PUT /api/dashboard/widgets/{id}/
```
- **Description**: Update a widget
- **Path Parameters**:
  - `id`: Widget ID
- **Request Body**: Widget fields to update
- **Response**: Updated widget object

```
DELETE /api/dashboard/widgets/{id}/
```
- **Description**: Delete a widget
- **Path Parameters**:
  - `id`: Widget ID
- **Response**: Success message

#### Layout Management

```
GET /api/dashboard/layouts/
```
- **Description**: List all dashboard layouts
- **Query Parameters**:
  - `created_by`: Filter by creator user ID
  - `is_default`: Filter by default status
- **Response**: List of layout objects

```
POST /api/dashboard/layouts/
```
- **Description**: Create a new dashboard layout
- **Request Body**:
  - `name`: Layout name (required)
  - `description`: Layout description (optional)
  - `widgets`: Array of widget placement objects (required)
  - `is_default`: Whether this is the default layout (default: false)
- **Response**: Created layout object

```
GET /api/dashboard/layouts/{id}/
```
- **Description**: Retrieve a specific layout
- **Path Parameters**:
  - `id`: Layout ID
- **Response**: Layout object with widget placements

```
PUT /api/dashboard/layouts/{id}/
```
- **Description**: Update a layout
- **Path Parameters**:
  - `id`: Layout ID
- **Request Body**: Layout fields to update
- **Response**: Updated layout object

```
DELETE /api/dashboard/layouts/{id}/
```
- **Description**: Delete a layout
- **Path Parameters**:
  - `id`: Layout ID
- **Response**: Success message

#### User Preferences

```
GET /api/dashboard/preferences/
```
- **Description**: Get dashboard preferences for the current user
- **Response**: User preference object

```
POST /api/dashboard/preferences/
```
- **Description**: Create or update dashboard preferences for the current user
- **Request Body**:
  - `layout_id`: Layout ID (required)
  - `custom_settings`: Custom settings JSON (optional)
- **Response**: Created or updated preference object

```
PUT /api/dashboard/preferences/reset/
```
- **Description**: Reset dashboard preferences to default for the current user
- **Response**: Updated preference object with default settings

#### Dashboard Overview

```
GET /api/dashboard/overview/
```
- **Description**: Get overview dashboard data
- **Response**: Overview dashboard data with key metrics

```
GET /api/dashboard/applications/
```
- **Description**: Get application-specific dashboard data
- **Query Parameters**:
  - `period`: Time period for data (day, week, month, year)
  - `status`: Filter by application status
- **Response**: Application dashboard data with metrics

```
GET /api/dashboard/documents/
```
- **Description**: Get document-specific dashboard data
- **Query Parameters**:
  - `period`: Time period for data (day, week, month, year)
  - `document_type`: Filter by document type
- **Response**: Document dashboard data with metrics

```
GET /api/dashboard/entities/
```
- **Description**: Get entity-specific dashboard data (borrowers/brokers)
- **Query Parameters**:
  - `period`: Time period for data (day, week, month, year)
  - `entity_type`: Entity type (borrower, broker)
- **Response**: Entity dashboard data with metrics

### Data Models

#### DashboardMetric Model

```json
{
  "id": 1,
  "name": "active_applications",
  "display_name": "Active Applications",
  "description": "Number of currently active loan applications",
  "category": "application",
  "metric_type": "count",
  "value": 42,
  "string_value": null,
  "json_value": null,
  "last_updated": "2023-06-15T10:30:00Z",
  "is_active": true
}
```

#### DashboardWidget Model

```json
{
  "id": 1,
  "name": "application_status_chart",
  "display_name": "Application Status Distribution",
  "description": "Pie chart showing distribution of application statuses",
  "widget_type": "chart_pie",
  "metrics": [
    {
      "id": 1,
      "name": "active_applications",
      "display_name": "Active Applications",
      "category": "application",
      "value": 42
    },
    {
      "id": 2,
      "name": "approved_applications",
      "display_name": "Approved Applications",
      "category": "application",
      "value": 18
    }
  ],
  "configuration": {
    "colors": ["#4287f5", "#42f5a7", "#f54242"],
    "legend": true,
    "donut": false
  },
  "position_x": 0,
  "position_y": 0,
  "width": 2,
  "height": 2,
  "is_active": true,
  "created_by": {
    "id": 1,
    "username": "admin"
  },
  "created_at": "2023-05-15T09:20:00Z",
  "updated_at": "2023-06-01T11:30:00Z"
}
```

#### DashboardLayout Model

```json
{
  "id": 1,
  "name": "Default Dashboard",
  "description": "Standard dashboard layout for loan officers",
  "is_default": true,
  "created_by": {
    "id": 1,
    "username": "admin"
  },
  "created_at": "2023-05-15T09:30:00Z",
  "updated_at": "2023-05-15T09:30:00Z",
  "widgets": [
    {
      "widget": {
        "id": 1,
        "name": "application_status_chart",
        "display_name": "Application Status Distribution",
        "widget_type": "chart_pie"
      },
      "position_x": 0,
      "position_y": 0,
      "width": 2,
      "height": 2
    },
    {
      "widget": {
        "id": 2,
        "name": "recent_applications",
        "display_name": "Recent Applications",
        "widget_type": "list"
      },
      "position_x": 2,
      "position_y": 0,
      "width": 2,
      "height": 3
    }
  ]
}
```

#### UserDashboardPreference Model

```json
{
  "id": 1,
  "user": {
    "id": 5,
    "username": "loan_officer"
  },
  "layout": {
    "id": 1,
    "name": "Default Dashboard"
  },
  "custom_settings": {
    "theme": "light",
    "refresh_interval": 300,
    "collapsed_widgets": [3, 5]
  }
}
```

## Error Handling

The Dashboard API uses standard HTTP status codes and provides detailed error messages:

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
- **Audit Logging**: All dashboard configuration changes are logged with user information

## Performance Considerations

- **Data Aggregation**: Pre-calculation of metrics to avoid expensive real-time calculations
- **Caching**: Aggressive caching of dashboard data with appropriate invalidation
- **Query Optimization**: Optimized queries for metric calculation
- **Background Processing**: Scheduled background tasks for metric updates
- **Pagination**: All list endpoints support pagination to handle large datasets

## Implementation Notes

- The Dashboard API is implemented using Django and Django REST Framework
- Metric calculations use Django's ORM for database aggregations
- Background tasks use Celery for scheduled metric updates
- Caching uses Redis for high-performance data storage
- API endpoints follow RESTful design principles
