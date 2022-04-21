from socket import AF_INET, AF_INET6, getaddrinfo
from typing import List

from fast_mda_traceroute.typing import AddressFamily

AF = {AddressFamily.Any: 0, AddressFamily.IPv4: AF_INET, AddressFamily.IPv6: AF_INET6}


def resolve(host: str, af: AddressFamily) -> List[str]:
    info = getaddrinfo(host, None, AF[af])
    return list(set(addr for _, _, _, _, (addr, *_) in info))
