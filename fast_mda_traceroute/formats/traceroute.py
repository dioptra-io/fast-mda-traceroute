from typing import List

from more_itertools import map_reduce
from pycaracal import Reply


def format_traceroute(replies: List[Reply]) -> str:
    # TODO: Print min/max/std RTT?
    if not replies:
        return ""
    destination_replies = [
        x for x in replies if x.destination_unreachable or x.echo_reply
    ]
    destination_ttl = 255
    if destination_replies:
        destination_ttl = min(x.probe_ttl for x in destination_replies)
    nodes_by_ttl = map_reduce(
        replies, lambda x: x.probe_ttl, lambda x: x.reply_src_addr, set
    )
    output = ""
    for ttl in range(min(nodes_by_ttl), min(max(nodes_by_ttl), destination_ttl) + 1):
        output += f"{ttl} "
        output += " ".join(nodes_by_ttl.get(ttl, []))
        output += "\n"
    return output.strip()
