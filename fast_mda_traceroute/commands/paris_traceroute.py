from math import ceil

from fast_mda_traceroute.typing import Protocol


def paris_traceroute_command(
    dst_addr: str,
    probing_rate: int,
    protocol: Protocol,
    min_ttl: int,
    max_ttl: int,
    src_port: int,
    dst_port: int,
    wait: int,
) -> str:
    protocol_flag = {Protocol.ICMP: "--icmp", Protocol.UDP: "--udp"}
    cmd = [
        "paris-traceroute",
        "--algorithm",
        "mda",
        "--src-port",
        src_port,
        "--dst-port",
        dst_port,
        protocol_flag[protocol],
        "--first",
        min_ttl,
        "--max-hops",
        max_ttl,
        "-q",
        1,
        "-w",
        ceil(wait / 1000),
        dst_addr,
    ]
    return " ".join(str(x) for x in cmd)
