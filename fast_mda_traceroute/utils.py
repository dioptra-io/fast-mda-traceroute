from ipaddress import ip_address

from diamond_miner.typing import Probe as DiamondMinerProbe
from pycaracal import Probe as CaracalProbe
from pycaracal import cast_addr, make_probe


def cast_probe(probe: DiamondMinerProbe) -> CaracalProbe:
    addr, src_port, dst_port, ttl, protocol = probe
    return make_probe(cast_addr(ip_address(addr)), src_port, dst_port, ttl, protocol)
