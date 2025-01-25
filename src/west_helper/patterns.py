import os
import yaml
from datetime import datetime
from typing import Dict, List, TypedDict

from .constants import DO_NOT_PASS_THRU_PATTERNS, PENDING_RESOLUTION_FILE, PATTERN_FILE
from .utils import print_message


class ErrorPattern(TypedDict):
    message: str
    resolution: List[str]
    pattern: str


def verify_data_integrity(expected_data, actual_data, file_path):
    print_message(f"Verifying data integrity for {file_path}")
    mismatches = []
    for key in expected_data:
        if key not in actual_data:
            mismatches.append(f"Missing key: {key}")
        elif expected_data[key] != actual_data[key]:
            mismatches.append(f"Value mismatch for key: {key}")

    if mismatches:
        print_message(f"Verification failed for {file_path}:")
        for mismatch in mismatches:
            print_message(f"   - {mismatch}")
    else:
        print_message(f"Successfully verified {file_path}")


def load_error_patterns() -> Dict[str, ErrorPattern]:
    patterns = {}
    if os.path.exists(PATTERN_FILE):
        try:
            with open(PATTERN_FILE, 'r') as f:
                patterns = yaml.safe_load(f)
            print_message(f"Loaded patterns from {PATTERN_FILE}")
        except (yaml.YAMLError, FileNotFoundError) as e:
            print_message(f"Error loading {PATTERN_FILE}: {e}")
    return patterns


def save_error_patterns(patterns: Dict[str, ErrorPattern], filepath: str) -> None:
    try:
        with open(filepath, 'w') as f:
            yaml.dump(patterns, f, default_flow_style=False)
        print_message(f"Saved patterns to {filepath}")
    except Exception as e:
        print_message(f"Error saving to {filepath}: {e}")


def rename_existing_pending_resolution_file():
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
