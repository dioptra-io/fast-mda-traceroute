from collections import OrderedDict
from datetime import datetime
from typing import List

from pycaracal import Reply

from fast_mda_traceroute.links import get_replies_by_node_link
from fast_mda_traceroute.typing import IPAddress, Protocol
from fast_mda_traceroute.utils import format_addr

METHOD = {Protocol.ICMP: "icmp-echo", Protocol.UDP: "udp-sport"}


def format_reply(reply, initial_flow_id) -> dict:
    return OrderedDict(
        tx=OrderedDict(sec=0, usec=0),
        replyc=1,
        ttl=reply.probe_ttl,
        attempt=0,
        flowid=reply.probe_src_port - initial_flow_id + 1,
        replies=[
            OrderedDict(
                rx=OrderedDict(
                    sec=int(reply.capture_timestamp / 1e6),
                    usec=int(reply.capture_timestamp / 1e6 % 1 * 1e6),
                ),
                ttl=reply.reply_ttl,
                rtt=reply.rtt / 10,
                ipid=reply.reply_id,
                icmp_type=reply.reply_icmp_type,
                icmp_code=reply.reply_icmp_code,
                icmp_q_tos=0,
                icmp_q_ttl=reply.quoted_ttl,
            )
        ],
    )


def format_scamper_json(
    confidence: int,
    hostname: str,
    src_addr: IPAddress,
    dst_addr: IPAddress,
    protocol: Protocol,
    min_ttl: int,
    src_port: int,
    dst_port: int,
    wait: int,
    start_time: datetime,
    stop_time: datetime,
    probes_sent: dict,
    replies: List[Reply],
):
    """
    Scamper-like JSON output, with the fields in the same order.
    """
    replies_by_node_link = get_replies_by_node_link(replies)

    sc_nodes = []
    sc_link_count = 0

    # Scamper shows a flow ID starting at 1 for ICMP probes
    # (and uses the source port for UDP).
    initial_flow_id = 1
    if protocol == Protocol.ICMP:
        initial_flow_id = src_port

    for node_addr, links in replies_by_node_link.items():
        sc_links = []
        for link_addr, replies in links.items():
            sc_probes = [
                format_reply(reply, initial_flow_id) for reply in replies if reply
            ]
            sc_probes = sorted(sc_probes, key=lambda x: x["flowid"])
            sc_link = OrderedDict(addr=format_addr(link_addr))
            if sc_probes:
                sc_link["probes"] = sc_probes
            sc_links.append(sc_link)
            sc_link_count += 1
        sc_nodes.append(
            OrderedDict(
                addr=format_addr(node_addr),
                q_ttl=1,  # TODO
                linkc=len(sc_links),
                links=[sc_links],
            )
        )

    # TODO: Implement this logic in pycaracal + IPv6
    # Minimum IPv4 + ICMP size, without the encoded TTL
    probe_size = 20 + 10

    cycle_start = OrderedDict(
        type="cycle-start",
        list_name="default",
        id=0,
        hostname=hostname,
        start_time=int(start_time.timestamp()),
    )

    tracelb = OrderedDict(
        type="tracelb",
        version="0.1",  # Same as scamper
        userid=0,
        method=METHOD[protocol],
        src=format_addr(src_addr),
        dst=format_addr(dst_addr),
        # sport=src_port,
        # dport=dst_port,
        start=OrderedDict(
            sec=int(start_time.timestamp()),
            usec=start_time.microsecond,
            ftime=f"{start_time:%Y-%m-%d %H:%M:%S}",
        ),
        probe_size=probe_size,
        firsthop=min_ttl,
        attempts=1,
        confidence=confidence,
        tos=0,
        gaplimit=0,
        wait_timeout=wait / 1000,
        wait_probe=0,
        probec=sum(probes_sent.values()),
        probec_max=0,
        nodec=len(sc_nodes),
        linkc=sc_link_count,
    )

    if sc_nodes:
        tracelb["nodes"] = sc_nodes

    cycle_stop = OrderedDict(
        type="cycle-stop",
        list_name="default",
        id=0,
        hostname=hostname,
        stop_time=int(stop_time.timestamp()),
    )

    return [cycle_start, tracelb, cycle_stop]
