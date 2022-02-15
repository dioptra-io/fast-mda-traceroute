from dataclasses import dataclass, field
from ipaddress import IPv6Address
from typing import List, Tuple


@dataclass(frozen=True)
class MockReply:
    """A Python replica of the C++ reply object, for easier testing."""

    capture_timestamp: int = 0
    reply_src_addr: IPv6Address = IPv6Address("::")
    reply_dst_addr: IPv6Address = IPv6Address("::")
    reply_size: int = 0
    reply_ttl: int = 0
    reply_protocol: int = 0
    reply_icmp_type: int = 0
    reply_icmp_code: int = 0
    reply_mpls_labels: List[Tuple[int, int, int, int]] = field(default_factory=list)
    probe_dst_addr: IPv6Address = IPv6Address("::")
    probe_id: int = 0
    probe_size: int = 0
    probe_protocol: int = 0
    quoted_ttl: int = 0
    probe_src_port: int = 0
    probe_dst_port: int = 0
    probe_ttl: int = 0
    rtt: float = 0

    @classmethod
    def time_exceeded(
        cls,
        probe_protocol: int,
        probe_dst_addr: str,
        probe_src_port: int,
        probe_dst_port: int,
        probe_ttl: int,
        reply_src_addr: str,
    ):
        return MockReply(
            probe_protocol=probe_protocol,
            probe_dst_addr=IPv6Address(probe_dst_addr),
            probe_src_port=probe_src_port,
            probe_dst_port=probe_dst_port,
            probe_ttl=probe_ttl,
            reply_src_addr=IPv6Address(reply_src_addr),
        )
