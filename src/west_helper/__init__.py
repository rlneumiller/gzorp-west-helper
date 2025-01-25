"""
west_helper: A helper utility for Zephyr's west command

This package provides utilities to:
- Monitor west build/flash operations
- Capture and match error patterns
- Provide resolutions for known issues
- Save build configurations
"""

from .utils import print_message, compare_paths
from .main import (
    save_build_config,
)

from .environment import (
    verify_required_execution_environment,
)

from .patterns import (
    load_error_patterns,
    save_error_patterns
)

__version__ = "0.1.0"

__all__ = [
    "print_message",
    "compare_paths",
    "verify_required_execution_environment",
    "save_build_config",
    "load_error_patterns",
    "save_error_patterns"
]
