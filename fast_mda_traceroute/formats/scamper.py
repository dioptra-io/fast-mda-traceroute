from datetime import datetime
from typing import List

from pycaracal import Reply

from fast_mda_traceroute import __version__
from fast_mda_traceroute.links import get_replies_by_node_link
from fast_mda_traceroute.typing import IPAddress, Protocol
from fast_mda_traceroute.utils import format_addr

METHOD = {Protocol.ICMP: "icmp-echo", Protocol.UDP: "udp-sport"}


def format_reply(reply) -> dict:
    return dict(
        attempt=0,
        flowid=reply.probe_src_port,
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
        tx=dict(sec=0, usec=0),
    )


def format_scamper_json(
    confidence: int,
    destination: IPAddress,
    protocol: Protocol,
    min_ttl: int,
    src_port: int,
    dst_port: int,
    wait: int,
    start_time: datetime,
    probes_sent: dict,
    replies: List[Reply],
):
    replies_by_node_link = get_replies_by_node_link(replies)

    sc_nodes = []
    sc_link_count = 0

    for node_addr, links in replies_by_node_link.items():
        sc_links = []
        for link_addr, replies in links.items():
            sc_probes = [format_reply(reply) for reply in replies if reply]
            sc_link = dict(addr=format_addr(link_addr))
            if sc_probes:
                sc_link["probes"] = sc_probes
            sc_links.append(sc_link)
            sc_link_count += 1
        sc_nodes.append(
            dict(
                addr=format_addr(node_addr),
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
        linkc=sc_link_count,
        method=METHOD[protocol],
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
