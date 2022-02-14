from collections import defaultdict
from typing import List

from pycaracal import Reply
from tabulate import tabulate

from fast_mda_traceroute.links import is_destination_unreachable, is_echo_reply


def format_table(replies: List[Reply]) -> str:
    table = []
    for reply in sorted(replies, key=lambda x: x.probe_ttl):
        table.append(
            (
                reply.probe_ttl,
                reply.probe_src_port,
                reply.probe_dst_port,
                reply.probe_dst_addr.ipv4_mapped,
                reply.reply_src_addr.ipv4_mapped,
                f"{reply.rtt / 10}ms",
                reply.reply_mpls_labels,
            )
        )
    return tabulate(
        table,
        headers=(
            "TTL",
            "Src. port",
            "Dst. port",
            "Probe IP",
            "Reply IP",
            "RTT",
            "MPLS label stack",
        ),
    )


def format_traceroute(replies: List[Reply]) -> str:
    # TODO: Print min/max/std RTT?
    if not replies:
        return ""
    destination_replies = [
        x for x in replies if is_destination_unreachable(x) or is_echo_reply(x)
    ]
    destination_ttl = 255
    if destination_replies:
        destination_ttl = min(x.probe_ttl for x in destination_replies)
    nodes_by_ttl = defaultdict(set)
    for reply in replies:
        nodes_by_ttl[reply.probe_ttl].add(reply.reply_src_addr)
    output = ""
    for ttl in range(min(nodes_by_ttl), min(max(nodes_by_ttl), destination_ttl) + 1):
        output += f"{ttl} "
        output += " ".join(str(node.ipv4_mapped or node) for node in nodes_by_ttl[ttl])
        output += "\n"
    return output.strip()
