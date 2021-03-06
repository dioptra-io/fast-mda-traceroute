from math import ceil

from fast_mda_traceroute.typing import Protocol


def scamper_command(
    dst_addr: str,
    probing_rate: int,
    protocol: Protocol,
    min_ttl: int,
    max_ttl: int,
    src_port: int,
    dst_port: int,
    wait: int,
) -> str:
    method = {Protocol.ICMP: "icmp-echo", Protocol.UDP: "udp-sport"}
    tracelb_cmd = [
        "tracelb",
        "-P",
        method[protocol],
        "-s",
        src_port,
        "-d",
        dst_port,
        "-f",
        min_ttl,
        "-q",
        1,
        "-w",
        ceil(wait / 1000),
        dst_addr,
    ]
    tracelb_cmd_s = " ".join(str(x) for x in tracelb_cmd)
    scamper_cmd = [
        "scamper",
        "-p",
        probing_rate,
        "-O",
        "json",
        "-I",
        f'"{tracelb_cmd_s}"',
    ]
    return " ".join(str(x) for x in scamper_cmd)
