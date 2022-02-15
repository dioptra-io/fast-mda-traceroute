from enum import Enum
from ipaddress import IPv4Address, IPv6Address
from typing import Optional, Tuple, Union

from pycaracal import Reply

Flow = Tuple[int, IPv6Address, int, int]
"""The 4-tuple that influences the flow ID in per-flow load-balancing."""
IPAddress = Union[IPv4Address, IPv6Address]
"""An IPv4 or IPv6 address."""
Link = Tuple[int, Optional[IPv6Address], Optional[IPv6Address]]
"""A pair of IP address between two consecutive TTLs, for the same flow ID."""
Pair = Tuple[int, Optional[Reply], Optional[Reply]]
"""A pair of replies between two consecutive TTLs, for the same flow ID."""


class DestinationType(Enum):
    Address = "address"
    Prefix = "prefix"


class EquivalentCommand(Enum):
    ParisTraceroute = "paris-traceroute"
    Scamper = "scamper"


class LogLevel(Enum):
    Debug = "DEBUG"
    Info = "INFO"
    Warning = "WARNING"
    Error = "ERROR"
    Critical = "CRITICAL"


class OutputFormat(Enum):
    ScamperJSON = "scamper-json"
    Text = "text"


class Protocol(Enum):
    ICMP = "icmp"
    UDP = "udp"
