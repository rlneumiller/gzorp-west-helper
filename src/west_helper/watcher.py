import queue
import re
import sys
from typing import TextIO

from .constants import ERROR_PATTERNS
from .patterns import filter_output
from .utils import print_message


# Flag to track if any pattern was matched
pattern_matched = False


def stream_watcher(stream: TextIO, prefix: str, message_queue: queue.Queue) -> None:
    '''
    Watches a stream for output and checks for known error patterns
    '''
    global pattern_matched
    try:
        for line in iter(stream.readline, ''):
            line = line.rstrip()

            # Only process non-empty lines that pass the filter
            if line and filter_output(line):
                if prefix == 'stderr':
                    sys.stderr.write('\x1b[38;5;208m' + line + '\x1b[0m' + '\n')
                else:
                    sys.stdout.write(line + '\n')

                # Check for matching patterns
                for pattern_name, pattern in ERROR_PATTERNS.items():
                    if re.search(pattern['pattern'], line):
                        pattern_matched = True
                        message_queue.put((pattern_name, pattern))
                        break
    except Exception as e:
        print_message(f"Error in stream_watcher: {e}")
