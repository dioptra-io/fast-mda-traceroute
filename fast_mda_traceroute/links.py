from typing import List

from more_itertools import map_reduce
from pycaracal import Reply


def get_flow_id(reply: Reply):
    return (
        reply.probe_protocol,
        reply.probe_dst_addr,
        reply.probe_src_port,
        reply.probe_dst_port,
    )


def filter_replies(replies: List[Reply]) -> List[Reply]:
    return [
        x
        for x in replies
        if x.reply_protocol == 1 and x.reply_icmp_type == 11 and x.reply_icmp_code == 0
    ]
    pass


def get_links(replies: List[Reply]):
    links = []
    replies_by_flow = map_reduce(replies, get_flow_id)
    for flow_id, replies in replies_by_flow.items():
        replies_by_ttl = map_reduce(replies, lambda x: x.probe_ttl)
        for ttl in range(min(replies_by_ttl), max(replies_by_ttl)):
            # TODO: Discard flows with more than one reply per TTL.
            near = replies_by_ttl.get(ttl, [None])[0]
            far = replies_by_ttl.get(ttl, [None])[0]
            if near:
                near = near.reply_src_addr
            if far:
                far = far.reply_src_addr
            links.append((ttl, ttl + 1, near, far))
    return list(set(links))


def get_links_by_ttl(replies: List[Reply]):
    return map_reduce(get_links(replies), lambda x: x[0])
