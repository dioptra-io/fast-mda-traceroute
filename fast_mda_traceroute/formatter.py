from tabulate import tabulate


def format_scamper_json(replies):
    raise NotImplementedError


def format_table(replies):
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
