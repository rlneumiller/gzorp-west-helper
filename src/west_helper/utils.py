# Standard library imports
import hashlib
import os
import subprocess
from pathlib import Path
from typing import Union



# Third-party imports
import yaml

from .constants import ZEPHYR_PATTERN_FILE, PATTERNS_DIR, MESSAGE_PREFIX_TEXT, VERSION_FILE


def print_message(msg: str) -> None:
    """
    Format and print messages with aligned line breaks after <br>.

    Args:
        msg: String containing message with <br> tags for line breaks

    Examples:
        print_message("First line<br>Second line")
        # Outputs:
        west_helper: First line
                          Second line
    """

    prefix = f"\033[95m{MESSAGE_PREFIX_TEXT}\033[0m"
    padding = " " * len(MESSAGE_PREFIX_TEXT) + " "
    sentences = [s.strip() for s in msg.split('<br>') if s.strip()]

    if sentences:
        # Print first sentence with prefix
        print(f"{prefix} {sentences[0]}")
        # Print remaining sentences with padding
        for sentence in sentences[1:]:
            print(f"{padding}{sentence}")


def compare_paths(path1: Union[str, Path], path2: Union[str, Path]) -> bool:
    """
    Compare two paths and determine if they point to the same location

    Args:
        path1: First path string or Path object
        path2: Second path string or Path object
    Returns:
        bool: True if paths point to same location
    """
    try:
        # Convert to absolute paths and resolve any symlinks
        path1_abs = Path(path1).resolve()
        path2_abs = Path(path2).resolve()

        # Compare normalized paths
        if path1_abs == path2_abs:
            return True
        else:
            return False
    except (OSError, ValueError) as e:
        print_message(f"Error comparing paths: {e}")
        return False


def get_pattern_hash(s: str) -> str:
    '''Return MD5 hash of input string'''
    return hashlib.md5(s.encode()).hexdigest()


def ensure_default_pattern():
    '''Ensure default pattern file exists'''
    if not os.path.exists(PATTERNS_DIR):
        os.makedirs(PATTERNS_DIR)

    if not os.path.exists(ZEPHYR_PATTERN_FILE):
        default_pattern = {
            "e3b0c44298fc1c149afbf4c8996fb924": {
                "pattern": "This is a placeholder pattern",
                "message": "This is a placeholder message.",
                "resolution": [
                    "This is a placeholder resolution.",
                    "This is another placeholder resolution.",
                    "This is yet another placeholder resolution."
                ]
            }
        }

        with open(ZEPHYR_PATTERN_FILE, 'w', encoding='utf-8') as f:
            yaml.dump(default_pattern, f, default_flow_style=False)
            print_message(f"Created default pattern file: {ZEPHYR_PATTERN_FILE}")


def update_pattern_hashes():
    '''Update pattern hashes in pattern files'''
    print_message("Checking for pattern hashes that need updating...")
    ensure_default_pattern()
    modified_hashes = []
    for root, _, files in os.walk(PATTERNS_DIR):
        for file in files:
            if file.endswith('.yaml') or file.endswith('.yml'):
                file_path = os.path.join(root, file)

            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            updated_data = {}
            for pattern_key, pattern_value in data.items():
                if isinstance(pattern_value, dict) and 'pattern' in pattern_value:
                    pattern_text = pattern_value['pattern']
                    pattern_hash = get_pattern_hash(pattern_text)
                    if pattern_key != pattern_hash:
                        print_message(f"Updating pattern hash: {pattern_key} -> {pattern_hash}")
                        updated_data[pattern_hash] = pattern_value
                        modified_hashes.append((file_path, pattern_text, pattern_hash))
                    else:
                        updated_data[pattern_key] = pattern_value

            # Fix: Use dump() instead of safe_dump() and set sort_keys=False
            with open(file_path, 'w', encoding='utf-8') as f:
                print_message(f"Checking pattern hashes in {file_path}")
                yaml.dump(updated_data, f, default_flow_style=False, sort_keys=False)

    print_message(f"Updated {len(modified_hashes)} pattern hashes.")
    return modified_hashes


def verify_data_integrity(expected_data, actual_data, file_path):
    '''Verify data integrity between expected and actual data'''
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


def run_command(command):
    '''Run shell command and check for errors'''
    try:
        print_message(f"Running command: {command}")
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print_message(f"Command '{command}' went horribly wrong. Here's the error: {e}")
        raise


def read_version():
    '''Read version from file'''
    try:
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE, 'r', encoding='utf-8') as f:
                version = f.read().strip()
                print_message(f"Current version read from file: {version}")
                return version
        else:
            raise FileNotFoundError(f"\033[95mupdate_west_helper:\033[0m Version file not found: {VERSION_FILE}")
    except (OSError, FileNotFoundError) as e:
        print_message(f"Oh my! I'm terribly sorry to interrupt, but it appears that I've "
                      f"encountered a spot of difficulty while attempting to read my version "
                      f"file. Here's the error: {e}"
                      )
        raise


def write_version(version):
    '''Write version to file'''
    try:
        with open(VERSION_FILE, 'w', encoding='utf-8') as f:
            f.write(version)
            print_message(f"New version written to file: {version}")
    except OSError as e:
        print_message(f" I regret to inform that I've had a spot of difficulty writing "
                      f"the version file: Here's the error: {e}. "
                      f"I'm terribly sorry for the inconvenience."
                      )
        raise


def increment_version(version):
    '''Increment version number'''
    major, minor, patch = map(int, version.split('.'))
    patch += 1
    new_version = f"{major}.{minor}.{patch}"
    print_message(f" Incremented version: {new_version}")
    return new_version
