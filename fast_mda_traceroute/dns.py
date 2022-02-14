from ipaddress import ip_address
from socket import getaddrinfo
from typing import List

from fast_mda_traceroute.typing import IPAddress


def resolve(host: str) -> List[IPAddress]:
    info = getaddrinfo(host, None)
    return list(set(ip_address(addr) for _, _, _, _, (addr, *_) in info))
