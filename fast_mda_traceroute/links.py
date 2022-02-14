from typing import Iterable

from more_itertools import map_reduce
from pycaracal import Reply


def get_flow_id(reply: Reply):
    return (
        reply.probe_protocol,
        reply.probe_dst_addr,
        reply.probe_src_port,
        reply.probe_dst_port,
    )


def is_icmp_time_exceeded(reply: Reply) -> bool:
    return (reply.reply_protocol == 1 and reply.reply_icmp_type == 11) or (
        reply.reply_protocol == 58 and reply.reply_icmp_type == 3
    )


# TODO: Detect loop+amplification
def get_links(replies: Iterable[Reply]):
    links = []
    replies_by_flow = map_reduce(replies, get_flow_id)
    for flow_id, replies in replies_by_flow.items():
        replies_by_ttl = map_reduce(replies, lambda x: x.probe_ttl)
        for ttl in range(min(replies_by_ttl), max(replies_by_ttl)):
            # TODO: Discard flows with more than one reply per TTL.
            near = replies_by_ttl.get(ttl, [None])[0]
            far = replies_by_ttl.get(ttl, [None])[0]
            links.append((ttl, ttl + 1, near, far))
    return list(set(links))


def get_links_by_ttl(replies: Iterable[Reply]):
    return map_reduce(get_links(replies), lambda x: x[0])


# TODO: Refactor get_links instead.
def count_links_by_ttl(replies: Iterable[Reply]):
    links = []
    replies_by_flow = map_reduce(replies, get_flow_id)
    for flow_id, replies in replies_by_flow.items():
        replies_by_ttl = map_reduce(replies, lambda x: x.probe_ttl)
        for ttl in range(min(replies_by_ttl), max(replies_by_ttl)):
            # TODO: Discard flows with more than one reply per TTL.
            near = replies_by_ttl.get(ttl, [None])[0]
            if near:
                near = near.reply_src_addr
            far = replies_by_ttl.get(ttl, [None])[0]
            if far:
                far = far.reply_src_addr
            links.append((ttl, near, far))
    links_by_ttl = list(set(links))
    return {
        ttl: len({(near, far) for _, near, far in links})
        for ttl, links in map_reduce(links_by_ttl, lambda x: x[0]).items()
    }
