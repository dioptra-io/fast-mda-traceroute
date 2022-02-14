from ipaddress import IPv4Address, IPv6Address
from typing import Optional, Tuple, Union

Flow = Tuple[int, IPv6Address, int, int]
IPAddress = Union[IPv4Address, IPv6Address]
Link = Tuple[Optional[IPv6Address], Optional[IPv6Address]]
