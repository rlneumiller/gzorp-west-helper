''' constants.py '''
import re
import os

VERSION_FILE = os.path.expanduser("~/.config/west_helper/version.txt")
INSTALL_DIR = "/usr/local/bin"
OUR_CONFIG_DIR = os.path.expanduser("~/.config/west_helper")
PATTERNS_DIR = os.path.join(OUR_CONFIG_DIR, "patterns")
ZEPHYR_PATTERN_FILE = os.path.join(PATTERNS_DIR, "zephyr.yaml")
MESSAGE_PREFIX_TEXT = "west-helper: "

PATTERN_FILE = "~/.config/west_helper/patterns/zephyr.yaml"
PENDING_RESOLUTION_FILE = "~/.config/west_helper/patterns/zephyr-pending-resolution.yaml"
CONFIG_DIR = "~/.config/west_helper"
PATTERN_DIR = "~/.config/west_helper/patterns"

ERROR_PATTERNS = {}


''' 
Maybe we also need NUISANCE_PATTERNS or HIDE_THESE_PATTERNS or IGNORED_PATTERNS or SKIPPED_PATTERNS
Consider adding a category to the patterns to allow for more flexibility in filtering
'''
DO_NOT_PASS_THRU_PATTERNS = [

    re.compile(r"Serial port /dev/ttyS\d+"),
    re.compile(r"/dev/ttyS\d+ failed to connect: Could not open /dev/ttyS\d+, the port is busy or doesn't exist."),
    re.compile(r"\(Could not configure port: \(5, 'Input/output error'\)\)"),
    re.compile(r"_WindowOverflow4"),
    re.compile(r"_stext at \?\?:\?"),
]

JSON_LD_EXAMPLE_0 = '''{
    "@context": "https://schema.org/",
    "@type": "SoftwareSourceCode",
    "identifier": "882dd80ba32808f80a49ddb72adb3292",
    "pattern": "E (\\d+) phy_init: failed to allocate \\d+ bytes for RF calibration data",
    "message": "RF calibration data allocation failure",
    "resolution": [
        "Insufficient system heap memory available",
        "Add CONFIG_HEAP_MEM_POOL_SIZE=4096 to prj.conf (increase the value if it still occurs, presuming you have the memory available)"
    ]
}'''

JSON_LD_EXAMPLE_1 = '''{
  "description": "Collection of patterns for debugging and logfile analysis",
  "version": "1.0",
  "patterns": [
    {
      "@context": "https://schema.org/",
      "@type": "SoftwareSourceCode",
      "category": "Error",
      "identifier": "882dd80ba32808f80a49ddb72adb3292",
      "pattern": "E (\\d+) phy_init: failed to allocate \\d+ bytes for RF calibration data",
      "message": "RF calibration data allocation failure",
      "resolution": [
        "Insufficient system heap memory available",
        "Add CONFIG_HEAP_MEM_POOL_SIZE=4096 to prj.conf (increase the value if it still occurs, presuming you have the memory available)"
      ],
      "severity": "High",
      "tags": ["memory", "RF calibration", "allocation"]
    },
    {
      "@context": "https://schema.org/",
      "@type": "SoftwareSourceCode",
      "category": "Warning",
      "identifier": "1234567890abcdef1234567890abcdef",
      "pattern": "W (\\d+) wifi_init: failed to connect to network",
      "message": "WiFi connection failure",
      "resolution": [
        "Check if the WiFi network is available",
        "Ensure the correct WiFi credentials are provided"
      ],
      "severity": "Medium",
      "tags": ["WiFi", "connection", "network"]
    }
  ]
}
'''

JSON_LD_EXAMPLE_2 = '''{
  "description": "Dataset of patterns for debugging and logfile analysis, useful for ML/RL contexts",
  "version": "1.0",
  "patterns": [
    {
      "@context": "https://schema.org/",
      "@type": "SoftwareSourceCode",
      "category": "Error",
      "identifier": "882dd80ba32808f80a49ddb72adb3292",
      "pattern": "E (\\d+) phy_init: failed to allocate \\d+ bytes for RF calibration data",
      "message": "RF calibration data allocation failure",
      "resolution": [
        "Insufficient system heap memory available",
        "Add CONFIG_HEAP_MEM_POOL_SIZE=4096 to prj.conf (increase the value if it still occurs, presuming you have the memory available)"
      ],
      "severity": "High",
      "tags": ["memory", "RF calibration", "allocation"],
      "label": "memory_issue",
      "features": {
        "error_code": "E",
        "component": "phy_init",
        "failure_type": "allocation",
        "data_type": "RF calibration data"
      },
      "context": {
        "timestamp": "2023-10-01T12:00:00Z",
        "system_state": "initialization",
        "previous_errors": 2
      },
      "frequency": 35,
      "codebase": "ProjectA",
      "system_type": "embedded",
      "os": "Linux",
      "component": "RF",
      "subcomponent": "calibration",
      "scope": "memory"
    },
    {
      "@context": "https://schema.org/",
      "@type": "SoftwareSourceCode",
      "category": "Warning",
      "identifier": "1234567890abcdef1234567890abcdef",
      "pattern": "W (\\d+) wifi_init: failed to connect to network",
      "message": "WiFi connection failure",
      "resolution": [
        "Check if the WiFi network is available",
        "Ensure the correct WiFi credentials are provided"
      ],
      "severity": "Medium",
      "tags": ["WiFi", "connection", "network"],
      "label": "network_issue",
      "features": {
        "error_code": "W",
        "component": "wifi_init",
        "failure_type": "connection",
        "data_type": "network"
      },
      "context": {
        "timestamp": "2023-10-01T12:05:00Z",
        "system_state": "operational",
        "previous_errors": 0
      },
      "frequency": 20,
      "codebase": "ProjectB",
      "system_type": "server",
      "os": "Linux",
      "component": "network",
      "subcomponent": "WiFi",
      "scope": "connection"
    }
  ]
}
'''
JSON_LD_EXAMPLE_3 = '''{
  "description": "Enhanced dataset schema for debug/log pattern analysis",
  "version": "1.1",
  "patterns": [
    {
      "@context": "https://schema.org/",
      "@type": "SoftwareSourceCode",
      "category": "Error",
      "identifier": "882dd80ba32808f80a49ddb72adb3292",
      "pattern": "E (\\d+) phy_init: failed to allocate \\d+ bytes for RF calibration data",
      "message": "RF calibration data allocation failure",
      "resolution": [
        "Insufficient system heap memory available",
        "Add CONFIG_HEAP_MEM_POOL_SIZE=4096 to prj.conf (increase the value if it still occurs, presuming you have the memory available)"
      ],
      "severity": "High",
      "tags": ["memory", "RF calibration", "allocation"],
      "label": "memory_issue",
      "features": {
        "error_code": "E",
        "component": "phy_init",
        "failure_type": "allocation",
        "data_type": "RF calibration data"
      },
      "diagnostics": {
        "metrics": {},
        "traces": [],
        "state": {}
      },
      "context": {
        "timestamp": "2023-10-01T12:00:00Z",
        "system_state": "initialization",
        "previous_errors": 2,
        "environment": {
          "properties": {},
          "variables": {}
        }
      },
      "metadata": {
        "first_seen": "2023-10-01T12:00:00Z",
        "last_seen": "2023-10-01T12:00:00Z",
        "occurrence_count": 35,
        "affected_versions": [],
        "resolution_status": "open"
      }
    }
  ]
}
'''
