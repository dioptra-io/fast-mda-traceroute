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
