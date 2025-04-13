"""
Tests for dashboard cache utilities
"""
from django.test import TestCase
from django.core.cache import cache
import json

from dashboard.cache import (
    get_cache_key,
    cache_dashboard_data,
    get_cached_dashboard_data,
    invalidate_dashboard_cache
)


class DashboardCacheTestCase(TestCase):
    """
    Test case for dashboard cache utilities
    """
    
    def setUp(self):
        """
        Set up test data
        """
        # Clear cache
        cache.clear()
        
        # Test data
        self.test_data = {
            'metric1': 100,
            'metric2': 200,
            'nested': {
                'value1': 'test',
                'value2': 42
            }
        }
    
    def test_get_cache_key(self):
        """
        Test get_cache_key function
        """
        # Simple key
        key1 = get_cache_key('test')
        self.assertEqual(key1, 'dashboard:test')
        
        # Key with parameters
        params = {'param1': 'value1', 'param2': 42}
        key2 = get_cache_key('test', params)
        self.assertTrue(key2.startswith('dashboard:test:'))
        
        # Keys with same parameters should be identical
        params2 = {'param2': 42, 'param1': 'value1'}  # Same params, different order
        key3 = get_cache_key('test', params2)
        self.assertEqual(key2, key3)
        
        # Keys with different parameters should be different
        params3 = {'param1': 'value1', 'param2': 43}  # Different value
        key4 = get_cache_key('test', params3)
        self.assertNotEqual(key2, key4)
    
    def test_cache_dashboard_data(self):
        """
        Test cache_dashboard_data function
        """
        # Cache data
        result = cache_dashboard_data('test', self.test_data)
        self.assertTrue(result)
        
        # Verify that data is cached
        key = get_cache_key('test')
        cached_data = cache.get(key)
        self.assertEqual(cached_data, self.test_data)
        
        # Cache data with parameters
        params = {'param1': 'value1', 'param2': 42}
        result = cache_dashboard_data('test', self.test_data, params)
        self.assertTrue(result)
        
        # Verify that data is cached with parameters
        key = get_cache_key('test', params)
        cached_data = cache.get(key)
        self.assertEqual(cached_data, self.test_data)
    
    def test_get_cached_dashboard_data(self):
        """
        Test get_cached_dashboard_data function
        """
        # Cache data
        cache_dashboard_data('test', self.test_data)
        
        # Get cached data
        cached_data = get_cached_dashboard_data('test')
        self.assertEqual(cached_data, self.test_data)
        
        # Get non-existent data
        cached_data = get_cached_dashboard_data('nonexistent')
        self.assertIsNone(cached_data)
        
        # Cache data with parameters
        params = {'param1': 'value1', 'param2': 42}
        cache_dashboard_data('test', self.test_data, params)
        
        # Get cached data with parameters
        cached_data = get_cached_dashboard_data('test', params)
        self.assertEqual(cached_data, self.test_data)
        
        # Get cached data with wrong parameters
        wrong_params = {'param1': 'value1', 'param2': 43}
        cached_data = get_cached_dashboard_data('test', wrong_params)
        self.assertIsNone(cached_data)
    
    def test_invalidate_dashboard_cache(self):
        """
        Test invalidate_dashboard_cache function
        """
        # Cache data
        cache_dashboard_data('overview', self.test_data)
        
        # Verify that data is cached
        self.assertIsNotNone(get_cached_dashboard_data('overview'))
        
        # Invalidate cache
        invalidate_dashboard_cache('overview')
        
        # Verify that the cache is cleared
        self.assertIsNone(get_cached_dashboard_data('overview'))
