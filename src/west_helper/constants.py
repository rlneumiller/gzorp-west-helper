import re

PATTERN_FILE = "~/.config/west_helper/patterns/zephyr.yaml"
PENDING_RESOLUTION_FILE = "~/.config/west_helper/patterns/zephyr-pending-resolution.yaml"
CONFIG_DIR = "~/.config/west_helper"
PATTERN_DIR = "~/.config/west_helper/patterns"

ERROR_PATTERNS = {}

DO_NOT_PASS_THRU_PATTERNS = [
    re.compile(r"Serial port /dev/ttyS\d+"),
    re.compile(r"/dev/ttyS\d+ failed to connect: Could not open /dev/ttyS\d+, the port is busy or doesn't exist."),
    re.compile(r"\(Could not configure port: \(5, 'Input/output error'\)\)"),
    re.compile(r"_WindowOverflow4"),
    re.compile(r"_stext at \?\?:\?")
]
pattern_matched = False
