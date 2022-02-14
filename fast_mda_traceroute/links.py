from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple

from more_itertools import map_reduce
from pycaracal import Reply

from fast_mda_traceroute.typing import Flow, Link


# TODO: Move these functions to caracal?
def is_destination_unreachable(reply: Reply) -> bool:
    return (reply.reply_protocol == 1 and reply.reply_icmp_type == 3) or (
        reply.reply_protocol == 58 and reply.reply_icmp_type == 1
    )


def is_echo_reply(reply: Reply) -> bool:
    return (reply.reply_protocol == 1 and reply.reply_icmp_type == 0) or (
        reply.reply_protocol == 58 and reply.reply_icmp_type == 129
    )


def is_time_exceeded(reply: Reply) -> bool:
    return (reply.reply_protocol == 1 and reply.reply_icmp_type == 11) or (
        reply.reply_protocol == 58 and reply.reply_icmp_type == 3
    )


def get_flow(reply: Reply) -> Flow:
    return (
        reply.probe_protocol,
        reply.probe_dst_addr,
        reply.probe_src_port,
        reply.probe_dst_port,
    )


# TODO: Detect loop+amplification
def get_links_by_ttl(replies: List[Reply]) -> Dict[int, Set[Link]]:
    links = defaultdict(set)
    replies_by_flow = map_reduce(replies, get_flow)
    for flow_id, replies in replies_by_flow.items():
        replies_by_ttl = map_reduce(replies, lambda x: x.probe_ttl)
        for ttl in range(min(replies_by_ttl), max(replies_by_ttl)):
            # TODO: Discard flows with more than one reply per TTL.
            near_reply = replies_by_ttl.get(ttl, [None])[0]
            far_reply = replies_by_ttl.get(ttl, [None])[0]
            link = (
                near_reply.reply_src_addr if near_reply else None,
                far_reply.reply_src_addr if far_reply else None,
            )
            links[ttl].add(link)
    return links


def get_replies_by_link(
    replies: List[Reply],
) -> Dict[Link, List[Tuple[Optional[Reply], Optional[Reply]]]]:
    replies_by_link = defaultdict(list)
    replies_by_flow = map_reduce(replies, get_flow)
    for flow_id, replies in replies_by_flow.items():
        replies_by_ttl = map_reduce(replies, lambda x: x.probe_ttl)
        for ttl in range(min(replies_by_ttl), max(replies_by_ttl)):
            # TODO: Discard flows with more than one reply per TTL.
            near_reply = replies_by_ttl.get(ttl, [None])[0]
            far_reply = replies_by_ttl.get(ttl, [None])[0]
            link = (
                near_reply.reply_src_addr if near_reply else None,
                far_reply.reply_src_addr if far_reply else None,
            )
            replies_by_link[link].append((near_reply, far_reply))
    return replies_by_link
