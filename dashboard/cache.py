"""
Cache utilities for dashboard
"""
from django.core.cache import cache
from django.conf import settings
import hashlib
import json


def get_cache_key(prefix, params=None):
    """
    Generate a cache key based on prefix and parameters
    
    Args:
        prefix (str): Cache key prefix
        params (dict): Parameters to include in the cache key
        
    Returns:
        str: Cache key
    """
    if params:
        # Sort params to ensure consistent key generation
        param_str = json.dumps(params, sort_keys=True)
        key_hash = hashlib.md5(param_str.encode()).hexdigest()
        return f"dashboard:{prefix}:{key_hash}"
    return f"dashboard:{prefix}"


def cache_dashboard_data(prefix, data, params=None, timeout=None):
    """
    Cache dashboard data
    
    Args:
        prefix (str): Cache key prefix
        data (any): Data to cache
        params (dict): Parameters used to generate the data
        timeout (int): Cache timeout in seconds
        
    Returns:
        bool: True if data was cached successfully
    """
    if timeout is None:
        timeout = getattr(settings, 'DASHBOARD_CACHE_TIMEOUT', 300)  # Default 5 minutes
    
    key = get_cache_key(prefix, params)
    cache.set(key, data, timeout)
    return True


def get_cached_dashboard_data(prefix, params=None):
    """
    Get cached dashboard data
    
    Args:
        prefix (str): Cache key prefix
        params (dict): Parameters used to generate the data
        
    Returns:
        any: Cached data or None if not found
    """
    key = get_cache_key(prefix, params)
    return cache.get(key)


def invalidate_dashboard_cache(prefix=None):
    """
    Invalidate dashboard cache
    
    Args:
        prefix (str): Optional prefix to invalidate specific cache entries
        
    Returns:
        bool: True if cache was invalidated
    """
    # Since Django's cache backend doesn't have a keys() method,
    # we'll need to manually track and clear keys
    if prefix:
        cache.delete(f"dashboard:{prefix}")
    else:
        # Clear all dashboard keys we know about
        prefixes = ['overview', 'applications', 'documents', 'entities']
        for p in prefixes:
            cache.delete(f"dashboard:{p}")
    
    return True
