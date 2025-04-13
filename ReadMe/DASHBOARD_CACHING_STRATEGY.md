# Dashboard Caching Strategy

## Overview

The Dashboard module implements a comprehensive caching strategy to optimize performance and reduce database load. This document outlines the caching approach, configuration options, and best practices.

## Caching Architecture

### Cache Keys

Cache keys are generated using a consistent pattern to ensure uniqueness and easy invalidation:

```
dashboard:{prefix}:{hash}
```

Where:
- `prefix`: The type of data being cached (e.g., 'overview', 'applications', 'documents')
- `hash`: MD5 hash of the query parameters (if any)

Example:
```
dashboard:overview:d41d8cd98f00b204e9800998ecf8427e
```

### Cache Duration

Default cache duration is 5 minutes (300 seconds), configurable via the `DASHBOARD_CACHE_TIMEOUT` setting in `settings.py`.

### Cache Storage

The dashboard uses Django's cache framework, which supports multiple backends:

- Memory cache (default for development)
- Database cache
- File system cache
- Memcached (recommended for production)
- Redis (recommended for production)

## Implementation

### Cache Utilities

The dashboard module provides utility functions for working with the cache:

```python
# Get a cache key
key = get_cache_key('overview', {'days': 30})

# Cache data
cache_dashboard_data('overview', data, {'days': 30}, timeout=300)

# Retrieve cached data
data = get_cached_dashboard_data('overview', {'days': 30})

# Invalidate cache
invalidate_dashboard_cache('overview')  # Invalidate specific prefix
invalidate_dashboard_cache()  # Invalidate all dashboard cache
```

### Cached Endpoints

The following endpoints implement caching:

1. **Overview API**: `/api/dashboard/overview/`
2. **Application Dashboard API**: `/api/dashboard/applications/`
3. **Document Dashboard API**: `/api/dashboard/documents/`
4. **Entity Dashboard API**: `/api/dashboard/entities/`

### Cache Invalidation

Cache is automatically invalidated in the following scenarios:

1. **Data Changes**: When related data is created, updated, or deleted
2. **Manual Refresh**: When a user explicitly requests fresh data
3. **Time-based Expiration**: When the cache timeout is reached

Invalidation is implemented using Django signals to detect data changes:

```python
@receiver(post_save, sender=Application)
def invalidate_application_cache(sender, instance, **kwargs):
    invalidate_dashboard_cache('applications')
    invalidate_dashboard_cache('overview')
```

## Performance Considerations

### Query Optimization

Before caching, queries are optimized to minimize database load:

1. **Select Related**: Using `select_related()` and `prefetch_related()` to reduce database queries
2. **Aggregation**: Using database aggregation functions instead of Python-based aggregation
3. **Indexing**: Ensuring proper database indexes are in place for frequently queried fields

### Selective Caching

Not all data is cached. The caching strategy focuses on:

1. **Expensive Queries**: Queries that involve complex joins or aggregations
2. **Frequently Accessed Data**: Data that is accessed often by multiple users
3. **Relatively Static Data**: Data that doesn't change frequently

### Cache Warming

For critical dashboard components, cache warming is implemented to ensure data is available immediately after deployment or cache invalidation:

```python
def warm_dashboard_cache():
    """
    Pre-populate the cache with common dashboard queries
    """
    # Warm overview cache with default parameters
    overview_data = generate_overview_data({'days': 30})
    cache_dashboard_data('overview', overview_data, {'days': 30})
    
    # Warm application dashboard cache
    app_data = generate_application_dashboard_data({'days': 30})
    cache_dashboard_data('applications', app_data, {'days': 30})
```

## Monitoring and Debugging

### Cache Hit Rate

Cache hit rate is monitored to ensure the caching strategy is effective:

```
X-Cache-Status: HIT
X-Cache-Key: dashboard:overview:d41d8cd98f00b204e9800998ecf8427e
```

### Performance Metrics

Response time metrics are included in response headers:

```
X-Dashboard-Response-Time: 0.125s
X-Dashboard-Cache-Time: 0.002s
```

### Logging

Cache operations are logged for debugging purposes:

```
INFO Serving application dashboard from cache
INFO Cache miss for dashboard:documents:d41d8cd98f00b204e9800998ecf8427e
INFO Document dashboard data generated in 0.125s
```

## Configuration

### Settings

The following settings can be configured in `settings.py`:

```python
# Cache timeout in seconds (default: 5 minutes)
DASHBOARD_CACHE_TIMEOUT = 300

# Enable/disable caching
DASHBOARD_CACHE_ENABLED = True

# Cache key prefix
DASHBOARD_CACHE_KEY_PREFIX = 'dashboard'
```

### Cache Backend

For production environments, it's recommended to use Memcached or Redis:

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
```

## Best Practices

1. **Monitor Cache Size**: Ensure the cache doesn't grow too large
2. **Tune Cache Duration**: Adjust cache timeout based on data volatility
3. **Selective Invalidation**: Invalidate only the necessary cache entries
4. **Cache Versioning**: Use cache versioning for major data structure changes
5. **Graceful Degradation**: Fall back to uncached data if cache is unavailable
