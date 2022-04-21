from enum import Enum
from typing import Optional, Tuple

from pycaracal import Reply

Flow = Tuple[int, str, int, int]
"""The 4-tuple that influences the flow ID in per-flow load-balancing."""

Link = Tuple[int, Optional[str], Optional[str]]
"""A pair of IP address between two consecutive TTLs, for the same flow ID."""

Pair = Tuple[int, Optional[Reply], Optional[Reply]]
"""A pair of replies between two consecutive TTLs, for the same flow ID."""


class AddressFamily(Enum):
    Any = "any"
    IPv4 = "4"
    IPv6 = "6"


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
    Table = "table"
    Traceroute = "traceroute"


class Protocol(Enum):
    ICMP = "icmp"
    UDP = "udp"
