from datetime import datetime
from typing import List, Literal

from more_itertools import map_reduce
from pycaracal import Reply

from fast_mda_traceroute import __version__
from fast_mda_traceroute.links import get_replies_by_link
from fast_mda_traceroute.typing import IPAddress
from fast_mda_traceroute.utils import format_addr


def format_reply(reply: Reply) -> dict:
    return dict(
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

    replies_by_link = get_replies_by_link(replies)
    replies_by_link_by_node = map_reduce(replies_by_link.items(), lambda x: x[0][0])

    sc_nodes = []
    sc_links_count = 0
    for node, links in replies_by_link_by_node.items():
        sc_links = []
        for (_, far_addr), replies in links:
            sc_probes = [
                format_reply(far_reply) for _, far_reply in replies if far_reply
            ]
            sc_links.append(
                dict(
                    addr=format_addr(far_addr), probec=len(sc_probes), probes=sc_probes
                )
            )
            sc_links_count += 1
        sc_nodes.append(
            dict(
                addr=format_addr(node),
                q_ttl=1,  # TODO
                linkc=len(sc_links),
                links=[sc_links],
            )
        )

    return dict(
        attempts=1,
        confidence=confidence,
        sport=src_port,
        dport=dst_port,
        dst=format_addr(destination),
        firsthop=min_ttl,
        gaplimit=0,
        linkc=sc_links_count,
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
        wait_timeout=wait / 1000,
        nodec=len(sc_nodes),
        nodes=sc_nodes,
    )
