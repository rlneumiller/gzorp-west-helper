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
from .utils import get_pattern_hash, print_message, update_pattern_hashes


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
            f"There was an error attempting to save the previous builds' Kconfig generated file to "
            f"{config_filepath}: {e}<br>You might wanna get that looked at"
        )


def handle_west_command(args, message_queue, unmatched_error_message):
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
            error_hash = get_pattern_hash(pattern)
            new_patterns[error_hash] = {
                'pattern': pattern,
                'message': unmatched_error_message,
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
        print_message(f"No matching pattern found for the current {unmatched_error_message.lower()}.")


def handle_west_build(args, message_queue):
    app_source_dir = args[4]
    save_build_config(app_source_dir)
    handle_west_command(args, message_queue, 'Unmatched build error')


def handle_west_flash(args, message_queue):
    handle_west_command(args, message_queue, 'Unmatched flash error')


def handle_west_espressif_monitor(args, message_queue):
    print_message("Handling west espressif monitor command")
    handle_west_command(args, message_queue, 'Unmatched espressif monitor error')


def print_args(args):
    """Print received arguments safely"""
    message = "Checking if we can help with this command<br>Arguments received:<br>"
    print_message(f"Received {len(args)} arguments")
    for i, arg in enumerate(args):
        message += f"argv[{i}] '{arg}'<br>"
    print_message(message)


def pass_it_thru(args):
    """
    Pass command through to west without modification.

    Args:
        args: List of command arguments to pass to west
    """
    try:
        subprocess.run(['west'] + args[1:], check=True)
    except subprocess.CalledProcessError as e:
        print_message(f"West command failed with exit code {e.returncode}")
        sys.exit(e.returncode)


def main():
    message_queue = queue.Queue()
    verify_required_execution_environment()

    if not ZEPHYR_BASE:
        print_message("ERROR: ZEPHYR_BASE environment variable is not set.<br>"
                      "I'm designed to help with Zephyr's west utility, which requires a zephyr build environment:")
        sys.exit(1)

    if len(sys.argv) < 2:
        print_message("Nothing for us to do here. Passing thru.")
        subprocess.run(['west'], check=True)
        return

    print_args(sys.argv)

    # Handle different west commands
    if sys.argv[1] == 'completion':
        # Pass completion commands directly to west
        pass_it_thru(sys.argv)
    elif len(sys.argv) > 4 and sys.argv[1] == 'build' and sys.argv[2] == '-b':
        handle_west_build(sys.argv, message_queue)
    elif len(sys.argv) > 2 and sys.argv[1] == 'flash':
        handle_west_flash(sys.argv, message_queue)
    elif len(sys.argv) > 2 and sys.argv[1] == 'espressif' and sys.argv[2] == 'monitor':
        handle_west_espressif_monitor(sys.argv, message_queue)
    else:
        print_message("Passing the command thru (not helping).")
        pass_it_thru(sys.argv)

    update_pattern_hashes()

if __name__ == "__main__":
    main()
