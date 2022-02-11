import logging
import sys
from ipaddress import ip_address
from random import randint
from typing import List

import click
from click_loglevel import LogLevel
from pycaracal import (
    Reply,
    cast_addr,
    experimental,
    make_probe,
    set_log_level,
    utilities,
)

from fast_mda_traceroute import __version__
from fast_mda_traceroute.algorithms import DiamondMinerLite
from fast_mda_traceroute.dns import resolve
from fast_mda_traceroute.formatter import format_scamper_json, format_table
from fast_mda_traceroute.logger import logger


@click.command()
@click.option(
    "--interface",
    metavar="INTERFACE",
    default=utilities.get_default_interface(),
    show_default=True,
    help="Network interface to use.",
)
@click.option(
    "--probing-rate",
    metavar="PPS",
    default=100,
    show_default=True,
    help="Probing rate in packets per second.",
)
@click.option(
    "--protocol",
    type=click.Choice(("icmp", "udp")),
    default="icmp",
    show_default=True,
    help="Protocol to use for the probe packets.",
)
@click.option(
    "--destination-type",
    type=click.Choice(("address", "prefix")),
    default="address",
    show_default=True,
    help="Whether to probe a single address, or the whole /24 or /64.",
)
@click.option(
    "--output-format",
    type=click.Choice(("text", "scamper-json")),
    default="text",
    show_default=True,
    help="Output format.",
)
@click.option(
    "--confidence",
    metavar="CONFIDENCE",
    type=click.IntRange(0, 99),
    default=95,
    show_default=True,
    help="Probability of discovering all the nodes at a given in TTL, in percent.",
)
@click.option(
    "--max-round",
    metavar="ROUNDS",
    type=click.IntRange(0),
    default=10,
    show_default=True,
    help="Maximum number of Diamond-Miner rounds.",
)
@click.option(
    "--wait",
    metavar="MILLISECONDS",
    type=click.IntRange(0),
    default=200,
    show_default=True,
    help="Time in milliseconds to wait for a reply.",
)
@click.option(
    "--min-ttl",
    metavar="TTL",
    type=click.IntRange(0, 255),
    default=1,
    show_default=True,
    help="Minimum TTL to probe.",
)
@click.option(
    "--max-ttl",
    metavar="TTL",
    type=click.IntRange(0, 255),
    default=32,
    show_default=True,
    help="Maximum TTL to probe.",
)
@click.option(
    "--src-port",
    metavar="PORT",
    type=click.IntRange(0, 65535),
    default=24000,
    show_default=True,
    help="Initial UDP source port or ICMP checksum value.",
)
@click.option(
    "--dst-port",
    metavar="PORT",
    type=click.IntRange(0, 65535),
    default=33434,
    show_default=True,
    help="UDP destination port. Not used for ICMP probes.",
)
@click.option(
    "--instance-id",
    metavar="ID",
    type=click.IntRange(0, 65535),
    default=randint(0, 65535),
    help="Identifier encoded in the packets to distinguish between multiple instances (random by default).",
)
@click.option(
    "--buffer-size",
    metavar="BYTES",
    type=click.IntRange(0),
    default=1024 * 1024,
    show_default=True,
    help="Receiver buffer size in bytes.",
)
@click.option(
    "--integrity-check/--no-integrity-check",
    is_flag=True,
    default=True,
    show_default=True,
    help="Whether to verify that replies match valid probes or not.",
)
@click.option(
    "--log-level",
    type=LogLevel(),
    default="INFO",
    show_default=True,
)
@click.option(
    "--version",
    is_flag=True,
    help="Print program version.",
)
@click.argument("destination")
def main(
    interface,
    probing_rate,
    protocol,
    destination_type,
    output_format,
    confidence,
    max_round,
    wait,
    min_ttl,
    max_ttl,
    src_port,
    dst_port,
    instance_id,
    buffer_size,
    integrity_check,
    log_level,
    version,
    destination,
):
    if version:
        print(f"fast-mda-traceroute {__version__}")
        return
    # TODO: Detect loop+amplification
    # TODO: dot/graphviz output
    logging.basicConfig(level=log_level, stream=sys.stdout)
    set_log_level(log_level)
    destination = resolve(destination)[0]
    logger.info(
        "destination=%s, interface=%s probing_rate=%d buffer_size=%d instance_id=%d integrity_check=%s",
        destination,
        interface,
        probing_rate,
        buffer_size,
        instance_id,
        integrity_check,
    )
    prober = experimental.Prober(
        interface, probing_rate, buffer_size, instance_id, integrity_check
    )
    dminer = DiamondMinerLite(
        ip_address(destination),
        min_ttl,
        max_ttl,
        src_port,
        dst_port,
        protocol,
        confidence,
        max_round,
    )
    all_replies: List[Reply] = []
    replies: List[Reply] = []
    while True:
        probes = [
            make_probe(cast_addr(ip_address(addr)), src_port, dst_port, ttl, protocol)
            for addr, src_port, dst_port, ttl, protocol in dminer.next_round(replies)
        ]
        logger.info("round=%d probes=%d", dminer.round, len(probes))
        if not probes:
            break
        replies = prober.probe(probes, wait)
        all_replies.extend(replies)
    if output_format == "scamper-json":
        print(format_scamper_json(all_replies))
    else:
        print(format_table(all_replies))
