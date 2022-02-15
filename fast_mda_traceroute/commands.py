from math import ceil

from fast_mda_traceroute.typing import IPAddress, Protocol
from fast_mda_traceroute.utils import format_addr


def get_paris_traceroute_command(
    destination: IPAddress,
    probing_rate: int,
    protocol: Protocol,
    min_ttl: int,
    max_ttl: int,
    src_port: int,
    dst_port: int,
    wait: int,
) -> str:
    if protocol == "icmp":
        protocol_flag = "--icmp"
    else:
        protocol_flag = "--udp"
    cmd = [
        "paris-traceroute",
        "--algorithm",
        "mda",
        "--src-port",
        src_port,
        "--dst-port",
        dst_port,
        protocol_flag,
        "--first",
        min_ttl,
        "--max-hops",
        max_ttl,
        "-q",
        1,
        "-w",
        wait / 1000,
        format_addr(destination),
    ]
    return " ".join(str(x) for x in cmd)


def get_scamper_command(
    destination: IPAddress,
    probing_rate: int,
    protocol: Protocol,
    min_ttl: int,
    max_ttl: int,
    src_port: int,
    dst_port: int,
    wait: int,
) -> str:
    if protocol == "icmp":
        method = "icmp-echo"
    else:
        method = "udp-sport"
    tracelb_cmd = [
        "tracelb",
        "-P",
        method,
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
        format_addr(destination),
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
