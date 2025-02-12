'''Patterns module'''
import os
from datetime import datetime
from typing import Dict, List, TypedDict

import yaml
from .constants import DO_NOT_PASS_THRU_PATTERNS, PENDING_RESOLUTION_FILE, PATTERN_FILE
from .utils import print_message


class ErrorPattern(TypedDict):
    '''ErrorPattern'''
    message: str
    resolution: List[str]
    pattern: str


def load_error_patterns() -> Dict[str, ErrorPattern]:
    ''' load_error_patterns '''
    patterns = {}
    if os.path.exists(PATTERN_FILE):
        try:
            with open(PATTERN_FILE, 'r', encoding='utf-8') as f:
                patterns = yaml.safe_load(f)
            print_message(f"Loaded patterns from {PATTERN_FILE}")
        except (yaml.YAMLError, FileNotFoundError) as e:
            print_message(f"Error loading {PATTERN_FILE}: {e}")
    return patterns


def save_error_patterns(patterns: Dict[str, ErrorPattern], filepath: str) -> None:
    ''' handle_west_command '''
    try:
        filepath = os.path.expanduser(filepath)

        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(patterns, f, default_flow_style=False)
        print_message(f"Saved patterns to {filepath}")
    except (yaml.YAMLError, OSError) as e:
        print_message(f"Error saving to {filepath}: {e}")


def rename_existing_pending_resolution_file():
    '''Rename existing pending resolution file if it exists'''
    print_message(f"Looking for existing pending resolution file {PENDING_RESOLUTION_FILE}")
    if os.path.exists(PENDING_RESOLUTION_FILE):
        print_message(f"Found existing pending resolution file {PENDING_RESOLUTION_FILE}")
        timestamp = datetime.now().strftime("%b-%d-%Y_%H:%M:%S")
        print_message(f"New name for pending resolution file: zephyr-pending-resolution.yaml-{timestamp}")
        new_name = f"{PENDING_RESOLUTION_FILE}-{timestamp}"
        os.rename(PENDING_RESOLUTION_FILE, new_name)
        print_message(f"Renamed existing pending resolution file to {new_name}")


def filter_output(line: str) -> bool:
    """
    Filter output lines based on DO_NOT_PASS_THRU_PATTERNS.
    Returns True if line should be shown (not filtered out).
    Returns False if line should be filtered out (not shown).
    """
    return not any(pattern.search(line) for pattern in DO_NOT_PASS_THRU_PATTERNS)
