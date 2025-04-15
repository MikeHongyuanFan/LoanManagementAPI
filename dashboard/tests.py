"""
Import all tests to make them discoverable by Django's test runner
"""

from dashboard.test_models import *
from dashboard.test_api import *
from dashboard.test_services import *
from dashboard.test_cache import *
from dashboard.test_performance import *
