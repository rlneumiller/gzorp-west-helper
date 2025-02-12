#!/usr/bin/env python3

import sys
import os
import subprocess
import threading
import queue
from datetime import datetime
import yaml
import filecmp
import hashlib  # Add to imports at top

from .config import ZEPHYR_BASE, GENERATED_KCONFIG_FILE
from .constants import PENDING_RESOLUTION_FILE
from .environment import verify_required_execution_environment
from .patterns import filter_output, save_error_patterns
from .watcher import stream_watcher
from .utils import get_pattern_hash, print_message, update_pattern_hashes


def save_build_config(app_source_dir: str) -> None:
    '''
    Save the Zephyr Kconfig generated build configuration file to the current application source directory
    with the purpose of comparing the previous .config with the any new .config after each build.

    Args:
        app_source_dir (str): The path to the application source directory.
    '''
    
    if not os.path.exists(app_source_dir):
        print_message(f"The app source folder appears to be missing {app_source_dir}<br>Something's not right.")
        sys.exit(1)

    if not os.path.exists(GENERATED_KCONFIG_FILE):
        # print_message(f"{GENERATED_KCONFIG_FILE} not found - can't save it if isn't there.<br>Skipping this step.")
        return

    # Find the most recently saved .config file
    saved_configs = [f for f in os.listdir(app_source_dir) if f.startswith('.config-')]
    
    if not saved_configs:
        print_message("No previous configs found - saving new config")
        save_dot_config(app_source_dir)
    else:
        # Sort configs by filename timestamp
        saved_configs.sort(key=parse_config_timestamp, reverse=True)
        most_recent_config = saved_configs[0]
        most_recent_config_path = os.path.join(app_source_dir, most_recent_config)
        
        # print_message(f"Comparing {GENERATED_KCONFIG_FILE} with most recent config: {most_recent_config_path}")
        
        if filecmp.cmp(most_recent_config_path, GENERATED_KCONFIG_FILE, shallow=False):
            print_message(f"Nothing new in {GENERATED_KCONFIG_FILE} - skipping save")
            return
        else:
            save_dot_config(app_source_dir)


def save_dot_config(app_source_dir: str) -> None:
        timestamp = datetime.now().strftime("%b-%d-%Y_%H:%M:%S")
        config_filename = f".config-{timestamp}"
        config_filepath = os.path.join(app_source_dir, config_filename)
        try:
            with open(GENERATED_KCONFIG_FILE, 'r') as src, open(config_filepath, 'w') as dst:
                dst.write(src.read())
            # print_message(f"Saved new config to {config_filepath}")
        except (OSError, IOError) as e:
            print_message(f"Error saving config: {e}")
        return        


def parse_config_timestamp(filename):
    """Parse timestamp from .config filename"""
    try:
        # Extract timestamp portion after .config-
        timestamp_str = filename.split('.config-')[1]
        return datetime.strptime(timestamp_str, "%b-%d-%Y_%H:%M:%S")
    except (IndexError, ValueError):
        return datetime.min


def handle_west_command(args, message_queue, unmatched_error_message):
    ''' handle_west_command '''
    process = subprocess.Popen(['west'] + args[1:], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout_thread = threading.Thread(target=stream_watcher, args=(process.stdout, 'stdout', message_queue))
    stderr_thread = threading.Thread(target=stream_watcher, args=(process.stderr, 'stderr', message_queue))
    stdout_thread.start()
    stderr_thread.start()
    
    try:
        process.wait()
    except KeyboardInterrupt:
        print_message("Process interrupted by user")
        process.terminate()
        stdout_thread.join()
        stderr_thread.join()
        return

    stdout_thread.join()
    stderr_thread.join()

    new_patterns = {}

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
                with open(PENDING_RESOLUTION_FILE, 'r', encoding='utf-8') as f:
                    existing_patterns = yaml.safe_load(f) or {}
            except (yaml.YAMLError, FileNotFoundError) as e:
                print_message(f"Error loading {PENDING_RESOLUTION_FILE}: {e}")
                existing_patterns = {}
            except (PermissionError) as e:
                print_message(f"Permission error reading {PENDING_RESOLUTION_FILE}: {e}")
                existing_patterns = {}
        else:
            existing_patterns = {}
            existing_patterns.update(new_patterns)
            save_error_patterns(existing_patterns, PENDING_RESOLUTION_FILE)


def handle_west_build(args, message_queue):
    ''' handle_west_build '''
    app_source_dir = args[4]
    
    handle_west_command(args, message_queue, 'Unmatched build error')
    save_build_config(app_source_dir)


def handle_west_flash(args, message_queue):
    ''' handle_west_flash '''
    handle_west_command(args, message_queue, 'Unmatched flash error')


def handle_west_espressif_monitor(args, message_queue):
    ''' handle_west_espressif_monitor '''
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
    '''Main function'''
    message_queue = queue.Queue()
    verify_required_execution_environment()

    if not ZEPHYR_BASE:
        print_message("ERROR: ZEPHYR_BASE environment variable is not set.<br>"
                      "I'm designed to help with Zephyr's west utility, which requires a zephyr build environment:")
        sys.exit(1)

    if len(sys.argv) < 2:
        # print_message("Nothing for us to do here. Passing thru.")
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
