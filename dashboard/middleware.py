"""
Middleware for dashboard performance monitoring
"""
import time
import logging
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('dashboard.performance')


class DashboardPerformanceMiddleware(MiddlewareMixin):
    """
    Middleware to monitor performance of dashboard API requests
    """
    
    def process_request(self, request):
        """
        Process request and set start time
        """
        if request.path.startswith('/api/dashboard/'):
            request.dashboard_start_time = time.time()
    
    def process_response(self, request, response):
        """
        Process response and log performance metrics
        """
        if hasattr(request, 'dashboard_start_time'):
            duration = time.time() - request.dashboard_start_time
            path = request.path
            method = request.method
            status_code = response.status_code
            
            # Log performance metrics
            logger.info(
                f"Dashboard API: {method} {path} - {status_code} - {duration:.3f}s"
            )
            
            # Add performance header to response
            response['X-Dashboard-Response-Time'] = f"{duration:.3f}s"
        
        return response
