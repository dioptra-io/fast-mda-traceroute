from enum import Enum
from ipaddress import IPv4Address, IPv6Address
from typing import Optional, Tuple, Union

Flow = Tuple[int, IPv6Address, int, int]
IPAddress = Union[IPv4Address, IPv6Address]
Link = Tuple[Optional[IPv6Address], Optional[IPv6Address]]


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
