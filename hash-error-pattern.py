
import hashlib

def hash_string(s: str) -> str:
    return hashlib.md5(s.encode()).hexdigest()

#pattern = "^devicetree error: .*: parse error: expected number or parenthesized expression"
#pattern = "^.*:\\d+: undefined reference to `usb_enable'"
#pattern = "warning: USB_CDC_ACM .* was assigned the value 'y' but got the value 'n'.*"
#pattern = ".*: warning: attempt to assign the value 'y' to the undefined symbol USB"
#pattern = ".*: warning: attempt to assign the value 'y' to the undefined symbol USB"
pattern = "warning: NET_L2_WIFI_MGMT .* has direct dependencies NETWORKING with value n, but is currently being y-selected by the following symbols:"
hashed_pattern = hash_string(pattern)
print(hashed_pattern)
