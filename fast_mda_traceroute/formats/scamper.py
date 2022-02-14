from collections import defaultdict
from datetime import datetime
from ipaddress import IPv6Address
from typing import Dict, List, Literal

from pycaracal import Reply

from fast_mda_traceroute import __version__
from fast_mda_traceroute.links import get_links_by_ttl
from fast_mda_traceroute.typing import IPAddress


def format_scamper_json(
    confidence: int,
    destination: IPAddress,
    protocol: Literal["icmp", "udp"],
    min_ttl: int,
    src_port: int,
    dst_port: int,
    wait: int,
    start_time: datetime,
    probes_sent: dict,
    replies: List[Reply],
):
    if protocol == "icmp":
        method = "icmp-echo"
    else:
        method = "udp-sport"

    replies_by_link: Dict[IPv6Address, Dict[IPv6Address, List[Reply]]] = defaultdict(
        lambda: defaultdict(list)
    )
    links = get_links_by_ttl(replies)
    for (_, _, near_reply, far_reply) in links:
        near_addr = near_reply.reply_src_addr if near_reply else "*"
        far_addr = far_reply.reply_src_addr if far_reply else "*"
        replies_by_link[near_addr][far_addr].append(far_reply)

    nodes = []
    for node, links in replies_by_link.items():
        n = dict(addr=str(node), linkc=len(links), links=[[]])
        for link, replies in links.items():
            lnk = dict(addr=str(link), probes=[])
            for reply in replies:
                if not reply:
                    continue
                lnk["probes"].append(
                    dict(
                        attempt=0,
                        flow_id=reply.probe_src_port,
                        replyc=1,
                        replies=[
                            dict(
                                icmp_type=reply.reply_icmp_type,
                                icmp_code=reply.reply_icmp_code,
                                icmp_q_tos=0,
                                icmp_q_ttl=reply.quoted_ttl,
                                ipid=0,
                                rtt=reply.rtt / 10,
                                rx=dict(
                                    sec=int(reply.capture_timestamp / 1e6),
                                    usec=int(reply.capture_timestamp / 1e6 % 1 * 1e6),
                                ),
                                ttl=reply.reply_ttl,
                            )
                        ],
                        ttl=reply.probe_ttl,
                        rx=dict(sec=0, usec=0),
                    )
                )
            lnk["probec"] = len(lnk["probes"])
            n["links"][0].append(lnk)
        nodes.append(n)

    return dict(
        attempts=1,
        confidence=confidence,
        sport=src_port,
        dport=dst_port,
        dst=str(destination),
        firsthop=min_ttl,
        gaplimit=0,
        linkc=len(links),
        method=method,
        probe_size=0,  # TODO
        probec=sum(probes_sent.values()),
        probec_max=0,
        src="0.0.0.0",  # TODO
        start=dict(
            ftime=f"{start_time:%y-%m-%d %H:%M:%S}",
            sec=int(start_time.timestamp()),
            usec=start_time.microsecond,
        ),
        tos=0,
        type="tracelb",
        userid=0,
        version=__version__,
        wait_probe=0,
        wait_timeout=wait / 10,
        nodec=len(nodes),
        nodes=nodes,
    )
