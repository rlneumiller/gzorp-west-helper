#!/usr/bin/env python3

import sys
import subprocess
import threading
import queue
import yaml
import os
from datetime import datetime

from .config import ZEPHYR_BASE, ZEPHYR_CONFIG_FILE
from .constants import PENDING_RESOLUTION_FILE
from .environment import verify_required_execution_environment
from .patterns import filter_output, save_error_patterns
from .watcher import stream_watcher
from .utils import hash_string, print_message

# CONFIG_DIR = os.path.expanduser('~/.config/west_helper')
# PATTERN_DIR = os.path.join(CONFIG_DIR, 'patterns')
# PATTERN_FILE = os.path.join(PATTERN_DIR, 'zephyr.yaml')
# PENDING_RESOLUTION_FILE = os.path.join(PATTERN_DIR, 'zephyr-pending-resolution.yaml')
# ZEPHYR_BASE = os.getenv('ZEPHYR_BASE')
# if ZEPHYR_BASE:
#    ZEPHYR_BUILD_DIR = os.path.join(ZEPHYR_BASE, 'build')
#    ZEPHYR_BUILD_ZEPHYR_DIR = os.path.join(ZEPHYR_BUILD_DIR, 'zephyr')
#    ZEPHYR_CONFIG_FILE = os.path.join(ZEPHYR_BUILD_ZEPHYR_DIR, '.config')


# Define the patterns to ignore
# DO_NOT_PASS_THRU_PATTERNS = [
#     # port related patterns
#     re.compile(r"Serial port /dev/ttyS\d+"),
#     re.compile(r"/dev/ttyS\d+ failed to connect: Could not open /dev/ttyS\d+, the port is busy or doesn't exist."),
#     re.compile(r"\(Could not configure port: \(5, 'Input/output error'\)\)"),
#     # Espressif specific patterns
#     re.compile(r"_WindowOverflow4"),
#     re.compile(r"_stext at \?\?:\?")
# ]


# TODO: Create PENDING_RESOLUTION_FILE if it does not exist
# TODO Rename the existing pending resolution file to [date-time]-zephyr-pending-resolution.yaml


pattern_matched_local = False


def save_build_config(app_source_dir: str) -> None:
    """
    Save the Zephyr build configuration file to the current application source directory
    with the purpose of comparing the previous .config with the any new .config after using menuconfig.

    Args:
        app_source_dir (str): The path to the application source directory.
    """
    if os.path.exists(app_source_dir):
        print_message(f"Building app source: {app_source_dir}")
    else:
        print_message(f"The app source appears to be missing {app_source_dir}<br>Something's not right.")
        print_message("Exiting.<br>Please try again.")
        sys.exit(1)

    if os.path.exists(ZEPHYR_CONFIG_FILE):
        pass
        # print_message(f"Found the previous builds' generated Kconfig file: {ZEPHYR_CONFIG_FILE}")
    else:
        print_message(f"{ZEPHYR_CONFIG_FILE} not found - can't save it if isn't there.<br>Skipping this step.")
        return

    timestamp = datetime.now().strftime("%b-%d-%Y_%H:%M:%S")
    config_filename = f".config-{timestamp}"
    config_filepath = os.path.join(app_source_dir, config_filename)
    try:
        with open(config_filepath, 'w') as f:
            # Copy the ZEPHYR_CONFIG_FILE file to the app source directory with the timestamped filename
            with open(ZEPHYR_CONFIG_FILE, 'r') as zephyr_config_file:
                f.write(zephyr_config_file.read())

        print_message(f"Copied previous builds' generated Kconfig file to {config_filepath}")
    except Exception as e:
        print_message(
            f"There was an error attempting to save the previous builds' Kconfig generated file to {config_filepath}: {e}<br>"
            "You might wanna get that looked at"
        )


def handle_west_build(args, message_queue):
    # Extracted from the "west build" block
    app_source_dir = args[4]
    save_build_config(app_source_dir)
    process = subprocess.Popen(['west'] + args[1:], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout_thread = threading.Thread(target=stream_watcher, args=(process.stdout, 'stdout', message_queue))
    stderr_thread = threading.Thread(target=stream_watcher, args=(process.stderr, 'stderr', message_queue))
    stdout_thread.start()
    stderr_thread.start()
    process.wait()
    stdout_thread.join()
    stderr_thread.join()

    new_patterns = {}
    # TODO: Load and utilize the existing patterns
    # previously_found_patterns = load_error_patterns()
    pattern_matched_local = False

    while not message_queue.empty():
        msg_type, data = message_queue.get()
        if msg_type == 'pattern_matched':
            pattern_matched_local = True
        else:
            pass

    if not pattern_matched_local:
        print_message("No matching pattern found for the current build error<br>")

    while not message_queue.empty():
        pattern_name, pattern = message_queue.get()
        if pattern_name == 'unmatched_error':
            error_hash = hash_string(pattern)
            new_patterns[error_hash] = {
                'pattern': pattern,
                'message': 'Unmatched build error',
                'resolution': [f'Resolution verification pending: {pattern}']
            }
            break
        else:
            if filter_output(pattern['message']):
                print_message(f"Matched pattern: {pattern_name}")
                print_message(f"Message: {pattern['message']}")
                print_message(f"Resolution: {pattern['resolution']}")

    if new_patterns:
        if os.path.exists(PENDING_RESOLUTION_FILE):
            try:
                with open(PENDING_RESOLUTION_FILE, 'r') as f:
                    existing_patterns = yaml.safe_load(f) or {}
            except (yaml.YAMLError, FileNotFoundError) as e:
                print_message(f"Error loading {PENDING_RESOLUTION_FILE}: {e}")
                existing_patterns = {}
        else:
            existing_patterns = {}

        existing_patterns.update(new_patterns)
        save_error_patterns(existing_patterns, PENDING_RESOLUTION_FILE)


def handle_west_flash(args, message_queue):
    # Extracted from the "west flash" block
    process = subprocess.Popen(['west'] + args[1:], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout_thread = threading.Thread(target=stream_watcher, args=(process.stdout, 'stdout', message_queue))
    stderr_thread = threading.Thread(target=stream_watcher, args=(process.stderr, 'stderr', message_queue))
    stdout_thread.start()
    stderr_thread.start()
    process.wait()
    stdout_thread.join()
    stderr_thread.join()

    new_patterns = {}
    pattern_matched_local = False

    while not message_queue.empty():
        pattern_name, pattern = message_queue.get()
        if pattern_name == 'unmatched_error':
            error_hash = hash_string(pattern)
            new_patterns[error_hash] = {
                'pattern': pattern,
                'message': 'Unmatched flash error',
                'resolution': [f'Resolution verification pending: {pattern}']
            }
            break
        else:
            if filter_output(pattern['message']):
                print_message(f"Matched pattern: {pattern_name}")
                print_message(f"Message: {pattern['message']}")
                print_message(f"Resolution: {pattern['resolution']}")

    if new_patterns:
        if os.path.exists(PENDING_RESOLUTION_FILE):
            try:
                with open(PENDING_RESOLUTION_FILE, 'r') as f:
                    existing_patterns = yaml.safe_load(f) or {}
            except (yaml.YAMLError, FileNotFoundError) as e:
                print_message(f"Error loading {PENDING_RESOLUTION_FILE}: {e}")
                existing_patterns = {}
        else:
            existing_patterns = {}
        existing_patterns.update(new_patterns)
        save_error_patterns(existing_patterns, PENDING_RESOLUTION_FILE)

    if not pattern_matched_local:
        print_message("No matching pattern found for the current flash error.")


def main():
    message_queue = queue.Queue()
    verify_required_execution_environment()

    if not ZEPHYR_BASE:
        print_message("ERROR: ZEPHYR_BASE environment variable is not set.<br>"
                      "I'm designed to help with Zephyr's west utility, which requires a zephyr build environment:")
        sys.exit(1)

    # Check if the command starts with "west build -b"
    print_message(f"Checking if we can help with this command<br>Arguments received:<br>argv[{0}] '{sys.argv[0]}<br>"
                  + f"argv[{1}] '{sys.argv[1]}<br>" + f"argv[{2}] '{sys.argv[2]}<br>"
                  + f"argv[{3}] '{sys.argv[3]}<br>" + f"argv[{4}] '{sys.argv[4]}<br>")

    if len(sys.argv) > 4 and sys.argv[1] == 'build' and sys.argv[2] == '-b':
        handle_west_build(sys.argv, message_queue)
    elif len(sys.argv) > 2 and sys.argv[2] == 'flash':
        handle_west_flash(sys.argv, message_queue)
    else:
        print_message("I'm passing the command thru (not helping).")

        # Run the west command
        subprocess.run(['west'] + sys.argv[1:], check=True)


if __name__ == "__main__":
    main()
