import re
import sys
from typing import TextIO
import queue


from .constants import ERROR_PATTERNS
from .patterns import filter_output
from .utils import print_message


def stream_watcher(stream: TextIO, prefix: str, message_queue: queue.SimpleQueue) -> None:
    '''
    Watches a stream for output and checks for known error patterns
    Utilizes SimpleQueue for inter-thread communication as SimpleQueue is both reentrant and thread-safe 
    '''
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
                matched = False
                for pattern_name, pattern in ERROR_PATTERNS.items():
                    if re.search(pattern['pattern'], line):
                        message_queue.put((pattern_name, pattern))
                        matched = True
                        break

                # Handle unmatched errors
                if not matched:
                    message_queue.put(('unmatched_error', line))

    except (IOError, OSError, ValueError) as e:
        print_message(f"Error in stream_watcher: {e}")

def process_unresolved_pattern(line: str) -> str:
    '''
    At this point the line (pattern) is known to not match any pattern we've seen before.
    Decides (somehow) if this new line (pattern) is potentially in need of a resolution and adds it to a list (or file) of unresolved patterns.
    '''
    for pattern_name, pattern in ERROR_PATTERNS.items():
        if re.search(pattern['pattern'], line):
            return pattern_name
    return 'unmatched_error'

'''
The idea is that each line of debug output is potentially useful.
1. We check if the line is in our list of lines to ignore.
2. IF it is not to be ignored, we check if the line is a known error pattern.
3. If it is a known error pattern, we tell the user what the resolution is.
4. If it is not a known error pattern, we add it to the message_queue for further processing.

Some function pulls a line from the message_queue and decides if it is in need of a resolution.
If it is, it adds it to the list of unresolved patterns..


Need to work out how to write a function or
functions to determine if a previously unseen line (pattern)
is potentially in need of a resolution. Bonus points if it can figure out how to resolve it.


Maybe we need more than one line to determine if a pattern is in need of a resolution, like a context. 
Some number of lines before and after the line in question.
'''