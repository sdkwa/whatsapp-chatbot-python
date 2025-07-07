"""Pytest configuration file."""

import sys
from unittest.mock import Mock

# Mock the SDKWA module before any tests run
sys.modules["sdkwa"] = Mock()

# Also mock the API client
mock_sdkwa = Mock()
mock_sdkwa.SDKWA = Mock()
sys.modules["sdkwa"] = mock_sdkwa
