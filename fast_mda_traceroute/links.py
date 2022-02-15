from collections import defaultdict
from ipaddress import IPv6Address
from typing import Dict, List, Optional, Set

from more_itertools import map_reduce
from pycaracal import Reply

from fast_mda_traceroute.typing import Flow, Link, Pair


def is_destination_unreachable(reply: Reply) -> bool:
    """Returns true if reply is an ICMP Destination Unreachable message."""
    return (reply.reply_protocol == 1 and reply.reply_icmp_type == 3) or (
        reply.reply_protocol == 58 and reply.reply_icmp_type == 1
    )


def is_echo_reply(reply: Reply) -> bool:
    """Returns true if reply is an ICMP Echo Reply message."""
    return (reply.reply_protocol == 1 and reply.reply_icmp_type == 0) or (
        reply.reply_protocol == 58 and reply.reply_icmp_type == 129
    )


def is_time_exceeded(reply: Reply) -> bool:
    """Returns true if reply is an ICMP Time Exceeded message."""
    return (reply.reply_protocol == 1 and reply.reply_icmp_type == 11) or (
        reply.reply_protocol == 58 and reply.reply_icmp_type == 3
    )


def get_flow(reply: Reply) -> Flow:
    """Returns the flow that triggered the reply."""
    # In the case of an ICMP Echo Reply message,
    # the probe destination address is equal to the reply source address.
    probe_dst_addr = (
        reply.reply_src_addr if is_echo_reply(reply) else reply.probe_dst_addr
    )
    return (
        reply.probe_protocol,
        probe_dst_addr,
        reply.probe_src_port,
        reply.probe_dst_port,
    )


def get_replies_by_flow(replies: List[Reply]) -> Dict[Flow, List[Reply]]:
    return map_reduce(replies, get_flow)


def get_pairs_by_flow(replies: List[Reply]) -> Dict[Flow, List[Pair]]:
    pairs_by_flow: Dict[Flow, List[Pair]] = defaultdict(list)
    replies_by_flow = get_replies_by_flow(replies)
    for flow, replies in replies_by_flow.items():
        replies_by_ttl = map_reduce(replies, lambda x: x.probe_ttl)
        for near_ttl in range(min(replies_by_ttl), max(replies_by_ttl)):
            near_replies = replies_by_ttl.get(near_ttl, [None])
            far_replies = replies_by_ttl.get(near_ttl + 1, [None])
            for near_reply in near_replies:
                for far_reply in far_replies:
                    pairs_by_flow[flow].append((near_ttl, near_reply, far_reply))
    return pairs_by_flow


def get_links_by_ttl(replies: List[Reply]) -> Dict[int, Set[Link]]:
    links_by_ttl = defaultdict(set)
    pairs_by_flow = get_pairs_by_flow(replies)
    for flow, pairs in pairs_by_flow.items():
        for near_ttl, near_reply, far_reply in pairs:
            links_by_ttl[near_ttl].add(
                (
                    near_ttl,
                    near_reply.reply_src_addr if near_reply else None,
                    far_reply.reply_src_addr if far_reply else None,
                )
            )
    return links_by_ttl


def get_replies_by_node_link(
    replies: List[Reply],
) -> Dict[Optional[IPv6Address], Dict[Optional[IPv6Address], List[Optional[Reply]]]]:
    """Data structure used in Scamper's JSON format."""
    replies_by_node_link: Dict[
        Optional[IPv6Address], Dict[Optional[IPv6Address], List[Optional[Reply]]]
    ] = defaultdict(lambda: defaultdict(list))
    pairs_by_flow = get_pairs_by_flow(replies)
    for flow, pairs in pairs_by_flow.items():
        for near_ttl, near_reply, far_reply in pairs:
            near_addr = near_reply.reply_src_addr if near_reply else None
            far_addr = far_reply.reply_src_addr if far_reply else None
            replies_by_node_link[near_addr][far_addr].append(far_reply)
    return replies_by_node_link
