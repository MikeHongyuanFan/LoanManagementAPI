# Dashboard Usage Examples

This document provides practical examples of how to use the Dashboard API for common scenarios.

## Table of Contents

1. [Authentication](#authentication)
2. [Retrieving Dashboard Overview](#retrieving-dashboard-overview)
3. [Working with Application Metrics](#working-with-application-metrics)
4. [Document Analytics](#document-analytics)
5. [Entity Insights](#entity-insights)
6. [Creating Custom Widgets](#creating-custom-widgets)
7. [Building Custom Layouts](#building-custom-layouts)
8. [Setting User Preferences](#setting-user-preferences)
9. [Error Handling](#error-handling)
10. [Performance Optimization](#performance-optimization)

## Authentication

Before making any API calls, you need to authenticate:

```javascript
// Using fetch API
async function getAuthToken() {
  const response = await fetch('/api/auth/token/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      username: 'your_username',
      password: 'your_password'
    })
  });
  
  const data = await response.json();
  return data.access;
}

// Store the token
const token = await getAuthToken();

// Use the token in subsequent requests
const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
};
```

## Retrieving Dashboard Overview

Get a comprehensive overview of all metrics:

```javascript
async function getDashboardOverview(days = 30) {
  const response = await fetch(`/api/dashboard/overview/?days=${days}`, {
    headers
  });
  
  return await response.json();
}

// Example usage
const overview = await getDashboardOverview();
console.log(`Total Applications: ${overview.loan_applications.total_applications}`);
console.log(`Total Documents: ${overview.documents.total_documents}`);
```

## Working with Application Metrics

Retrieve and analyze application metrics:

```javascript
async function getApplicationMetrics(days = 30) {
  const response = await fetch(`/api/dashboard/applications/?days=${days}`, {
    headers
  });
  
  return await response.json();
}

// Example usage
const appMetrics = await getApplicationMetrics();

// Plot applications over time
const dates = appMetrics.applications_over_time.map(item => item.date);
const counts = appMetrics.applications_over_time.map(item => item.count);

// Create a chart using your preferred library (e.g., Chart.js)
const chart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: dates,
    datasets: [{
      label: 'Applications',
      data: counts,
      borderColor: '#4CAF50'
    }]
  }
});

// Calculate approval rate
const statusCounts = appMetrics.applications_by_status;
const approved = statusCounts.find(s => s.status === 'approved')?.count || 0;
const total = statusCounts.reduce((sum, item) => sum + item.count, 0);
const approvalRate = (approved / total * 100).toFixed(1);

console.log(`Approval Rate: ${approvalRate}%`);
```

## Document Analytics

Analyze document metrics:

```javascript
async function getDocumentMetrics(days = 30) {
  const response = await fetch(`/api/dashboard/documents/?days=${days}`, {
    headers
  });
  
  return await response.json();
}

// Example usage
const docMetrics = await getDocumentMetrics();

// Create a pie chart of document types
const types = docMetrics.documents_by_type.map(item => item.document_type);
const typeCounts = docMetrics.documents_by_type.map(item => item.count);

const pieChart = new Chart(ctx, {
  type: 'pie',
  data: {
    labels: types,
    datasets: [{
      data: typeCounts,
      backgroundColor: ['#4CAF50', '#FFC107', '#F44336', '#2196F3']
    }]
  }
});

// Check documents pending approval
const pendingApproval = docMetrics.documents_by_status.find(
  s => s.status === 'pending_approval'
)?.count || 0;

if (pendingApproval > 0) {
  console.log(`Alert: ${pendingApproval} documents pending approval`);
}
```

## Entity Insights

Analyze borrower and broker metrics:

```javascript
async function getEntityMetrics(days = 30) {
  const response = await fetch(`/api/dashboard/entities/?days=${days}`, {
    headers
  });
  
  return await response.json();
}

// Example usage
const entityMetrics = await getEntityMetrics();

// Create a map of borrowers by state
const stateData = entityMetrics.borrowers_by_state;
createChoroplethMap('usa', stateData);

// Display top brokers
const topBrokers = entityMetrics.top_brokers;
const brokerTable = document.getElementById('top-brokers-table');

topBrokers.forEach(broker => {
  const row = brokerTable.insertRow();
  row.insertCell(0).textContent = `${broker.broker__first_name} ${broker.broker__last_name}`;
  row.insertCell(1).textContent = broker.application_count;
  row.insertCell(2).textContent = `$${(broker.total_loan_amount / 1000000).toFixed(2)}M`;
});
```

## Creating Custom Widgets

Create a custom dashboard widget:

```javascript
async function createWidget(widgetData) {
  const response = await fetch('/api/dashboard/widgets/', {
    method: 'POST',
    headers,
    body: JSON.stringify(widgetData)
  });
  
  return await response.json();
}

// Example usage
const newWidget = await createWidget({
  name: 'loan_amount_trend',
  display_name: 'Loan Amount Trend',
  description: 'Monthly trend of total loan amounts',
  widget_type: 'chart_line',
  configuration: {
    title: 'Monthly Loan Volume',
    height: 300,
    y_axis_label: 'Amount ($)',
    x_axis_label: 'Month',
    colors: ['#4CAF50']
  },
  position_x: 0,
  position_y: 0,
  width: 3,
  height: 2,
  metrics: [5, 8]  // IDs of relevant metrics
});

console.log(`Widget created with ID: ${newWidget.id}`);
```

## Building Custom Layouts

Create a custom dashboard layout:

```javascript
async function createLayout(layoutData) {
  const response = await fetch('/api/dashboard/layouts/', {
    method: 'POST',
    headers,
    body: JSON.stringify(layoutData)
  });
  
  return await response.json();
}

// Example usage
const newLayout = await createLayout({
  name: 'executive_dashboard',
  description: 'Executive overview dashboard',
  is_default: false
});

// Add widgets to the layout
async function addWidgetToLayout(layoutId, widgetData) {
  const response = await fetch(`/api/dashboard/layouts/${layoutId}/widgets/`, {
    method: 'POST',
    headers,
    body: JSON.stringify(widgetData)
  });
  
  return await response.json();
}

// Add widgets to the layout
await addWidgetToLayout(newLayout.id, {
  widget_id: 1,
  position_x: 0,
  position_y: 0,
  width: 2,
  height: 2
});

await addWidgetToLayout(newLayout.id, {
  widget_id: 2,
  position_x: 2,
  position_y: 0,
  width: 2,
  height: 1
});
```

## Setting User Preferences

Set user dashboard preferences:

```javascript
async function setUserPreferences(preferencesData) {
  // Check if preferences already exist
  const response = await fetch('/api/dashboard/preferences/', {
    headers
  });
  
  const existingPrefs = await response.json();
  
  if (existingPrefs.results.length > 0) {
    // Update existing preferences
    const prefId = existingPrefs.results[0].id;
    const updateResponse = await fetch(`/api/dashboard/preferences/${prefId}/`, {
      method: 'PATCH',
      headers,
      body: JSON.stringify(preferencesData)
    });
    
    return await updateResponse.json();
  } else {
    // Create new preferences
    const createResponse = await fetch('/api/dashboard/preferences/', {
      method: 'POST',
      headers,
      body: JSON.stringify(preferencesData)
    });
    
    return await createResponse.json();
  }
}

// Example usage
const preferences = await setUserPreferences({
  layout_id: 1,
  custom_settings: {
    theme: 'dark',
    refresh_interval: 60,
    default_date_range: 30
  }
});

console.log('User preferences saved');
```

## Error Handling

Handle API errors gracefully:

```javascript
async function fetchDashboardData(endpoint, params = {}) {
  try {
    // Build query string
    const queryString = Object.entries(params)
      .map(([key, value]) => `${key}=${value}`)
      .join('&');
    
    const url = `/api/dashboard/${endpoint}/${queryString ? '?' + queryString : ''}`;
    
    const response = await fetch(url, { headers });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP error ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Dashboard API error: ${error.message}`);
    
    // Show user-friendly error message
    showErrorNotification(`Failed to load dashboard data: ${error.message}`);
    
    // Return empty data structure
    return {};
  }
}
```

## Performance Optimization

Optimize dashboard performance:

```javascript
// Cache API responses in memory
const apiCache = new Map();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes in milliseconds

async function fetchWithCache(endpoint, params = {}) {
  // Generate cache key
  const queryString = Object.entries(params)
    .map(([key, value]) => `${key}=${value}`)
    .join('&');
  
  const cacheKey = `${endpoint}?${queryString}`;
  
  // Check if we have a valid cached response
  if (apiCache.has(cacheKey)) {
    const cachedData = apiCache.get(cacheKey);
    if (Date.now() < cachedData.expiry) {
      console.log(`Using cached data for ${cacheKey}`);
      return cachedData.data;
    }
  }
  
  // Fetch fresh data
  console.log(`Fetching fresh data for ${cacheKey}`);
  const data = await fetchDashboardData(endpoint, params);
  
  // Cache the response
  apiCache.set(cacheKey, {
    data,
    expiry: Date.now() + CACHE_TTL
  });
  
  return data;
}

// Example usage
const overviewData = await fetchWithCache('overview', { days: 30 });
```
