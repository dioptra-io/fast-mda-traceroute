from ipaddress import IPv4Address, IPv6Address, ip_address
from typing import Optional

from diamond_miner.typing import Probe as DiamondMinerProbe
from pycaracal import Probe as CaracalProbe
from pycaracal import cast_addr, make_probe

from fast_mda_traceroute.typing import IPAddress


def cast_probe(probe: DiamondMinerProbe) -> CaracalProbe:
    addr, src_port, dst_port, ttl, protocol = probe
    return make_probe(cast_addr(ip_address(addr)), src_port, dst_port, ttl, protocol)


def format_addr(addr: Optional[IPAddress]) -> str:
    if isinstance(addr, IPv4Address):
        return str(addr)
    if isinstance(addr, IPv6Address):
        return str(addr.ipv4_mapped or addr)
    return str(addr)
