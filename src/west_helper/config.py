# config.py: Contains the configuration for the west_helper module.
import os
import sys
from .utils import print_message

ZEPHYR_BASE = os.getenv('ZEPHYR_BASE')
if not ZEPHYR_BASE:
    print_message("ZEPHYR_BASE environment variable is not set and we wants it!<br>"
                  "Please set it to the root of the Zephyr repository.")
    sys.exit(1)

ZEPHYR_BUILD_DIR = os.path.join(ZEPHYR_BASE, 'build')
ZEPHYR_BUILD_ZEPHYR_DIR = os.path.join(ZEPHYR_BUILD_DIR, 'zephyr')
GENERATED_KCONFIG_FILE = os.path.join(ZEPHYR_BUILD_ZEPHYR_DIR, '.config')
