import os
import shutil
import sys

from .utils import print_message, compare_paths

ZEPHYR_BASE = os.getenv('ZEPHYR_BASE')


def verify_required_execution_environment():
    """
    Validate that west is available and that we are in a venv.
    """
    # Check virtual environment
    if sys.prefix == sys.base_prefix:  # If NOT in a virtual environment
        print_message("I require operating within a Python virtual environment. Exiting.")
        sys.exit(1)

    # Check west command availability
    if not shutil.which('west'):
        print_message("Did not find the west utility in the current environment<br> I can't help west without west<br> Exiting")
        sys.exit(1)

    # Ensure that the current working directory is the same as ZEPHYR_BASE
    validate_zephyr_environment()

    print_message("Verified that we are in a good place to help west")


def validate_zephyr_environment() -> None:
    """
    Validate Zephyr build environment settings.
    """
    current_dir = os.path.abspath(os.getcwd())

    if ZEPHYR_BASE is None:
        raise EnvironmentError(
            "ZEPHYR_BASE environment variable is not set."
            "Please initialize Zephyr build environment first."
        )

    zephyr_base_dir = os.path.abspath(ZEPHYR_BASE)
    if not compare_paths(current_dir, zephyr_base_dir):
        raise ValueError(
            f"Current directory ({current_dir}) must be "
            f"ZEPHYR_BASE ({zephyr_base_dir})"
        )
