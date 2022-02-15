import json
import logging
import sys
from datetime import datetime
from ipaddress import ip_address
from random import randint
from typing import Optional

import typer
from more_itertools import flatten
from pycaracal import experimental, log_to_stderr, set_log_level, utilities

from fast_mda_traceroute import __version__
from fast_mda_traceroute.algorithms import DiamondMiner
from fast_mda_traceroute.commands import (
    get_paris_traceroute_command,
    get_scamper_command,
)
from fast_mda_traceroute.dns import resolve
from fast_mda_traceroute.formats import format_scamper_json
from fast_mda_traceroute.formats.text import format_traceroute
from fast_mda_traceroute.links import get_links_by_ttl
from fast_mda_traceroute.logger import logger
from fast_mda_traceroute.typing import (
    DestinationType,
    EquivalentCommand,
    LogLevel,
    OutputFormat,
    Protocol,
)
from fast_mda_traceroute.utils import cast_probe

app = typer.Typer()


def version_callback(value: bool):
    if value:
        print(f"fast-mda-traceroute {__version__}")
        raise typer.Exit()


@app.command()
def main(
    interface: str = typer.Option(
        utilities.get_default_interface(),
        metavar="INTERFACE",
        help="Network interface to use.",
    ),
    probing_rate: int = typer.Option(
        100,
        metavar="PPS",
        help="Probing rate in packets per second.",
    ),
    protocol: Protocol = typer.Option(
        Protocol.ICMP.value,
        help="Protocol to use for the probe packets.",
    ),
    destination_type: DestinationType = typer.Option(
        DestinationType.Address.value,
        help="Whether to probe a single address, or the whole /24 or /64.",
    ),
    format: OutputFormat = typer.Option(
        OutputFormat.Text.value,
        help="Output format.",
    ),
    confidence: int = typer.Option(
        95,
        min=0,
        max=99,
        metavar="CONFIDENCE",
        help="Probability of discovering all the nodes at a given in TTL, in percent.",
    ),
    max_round: int = typer.Option(
        10,
        min=0,
        metavar="ROUNDS",
        help="Maximum number of Diamond-Miner rounds.",
    ),
    wait: int = typer.Option(
        200,
        min=0,
        metavar="MILLISECONDS",
        help="Time in milliseconds to wait for a reply.",
    ),
    min_ttl: int = typer.Option(
        1,
        min=0,
        max=255,
        metavar="TTL",
        help="Minimum TTL to probe.",
    ),
    max_ttl: int = typer.Option(
        32,
        min=0,
        max=255,
        metavar="TTL",
        help="Maximum TTL to probe.",
    ),
    src_port: int = typer.Option(
        24000,
        min=0,
        max=65535,
        metavar="PORT",
        help="Initial UDP source port or ICMP checksum value.",
    ),
    dst_port: int = typer.Option(
        33434,
        min=0,
        max=65535,
        metavar="PORT",
        help="UDP destination port. Not used for ICMP probes.",
    ),
    instance_id: int = typer.Option(
        randint(0, 65535),
        min=0,
        max=65535,
        metavar="ID",
        help="Identifier encoded in the packets to distinguish between multiple instances (random by default).",
        show_default=False,
    ),
    buffer_size: int = typer.Option(
        1024 * 1024,
        min=0,
        metavar="BYTES",
        help="Receiver buffer size in bytes.",
    ),
    integrity_check: bool = typer.Option(
        True,
        help="Whether to verify that replies match valid probes or not.",
    ),
    log_level: LogLevel = typer.Option(
        LogLevel.Info.value,
        case_sensitive=False,
    ),
    print_command: Optional[EquivalentCommand] = typer.Option(
        None,
        help="Print equivalent command and exit.",
    ),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=version_callback,
        help="Print program version.",
    ),
    destination: str = typer.Argument(..., help="Destination hostname or IP address."),
):
    # Configure Python logger
    logging.basicConfig(
        format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        level=log_level.value,
        stream=sys.stderr,
    )

    # Configure Caracal's C++ logger (spdlog)
    log_to_stderr()
    set_log_level(logging.getLevelName(log_level.value))

    destination_addr = resolve(destination)[0]
    logger.info(
        "destination_addr=%s, interface=%s probing_rate=%d buffer_size=%d instance_id=%d integrity_check=%s version=%s",
        destination_addr,
        interface,
        probing_rate,
        buffer_size,
        instance_id,
        integrity_check,
        __version__,
    )

    if print_command:
        args = (
            destination_addr,
            probing_rate,
            protocol,
            min_ttl,
            max_ttl,
            src_port,
            dst_port,
            wait,
        )
        if print_command == EquivalentCommand.ParisTraceroute:
            print(get_paris_traceroute_command(*args))
        else:
            print(get_scamper_command(*args))
        raise typer.Exit()

    prober = experimental.Prober(
        interface, probing_rate, buffer_size, instance_id, integrity_check
    )
    dminer = DiamondMiner(
        ip_address(destination_addr),
        min_ttl,
        max_ttl,
        src_port,
        dst_port,
        protocol.value,
        confidence,
        max_round,
    )

    start_time = datetime.now()
    last_replies = []
    while True:
        probes = [cast_probe(x) for x in dminer.next_round(last_replies)]
        links_found = len(set(flatten(get_links_by_ttl(dminer.all_replies()).values())))
        logger.info(
            "round=%d links_found=%d probes=%d expected_time=%.1fs",
            dminer.current_round,
            links_found,
            len(probes),
            len(probes) / probing_rate,
        )
        if not probes:
            break
        last_replies = prober.probe(probes, wait)

    if format == OutputFormat.ScamperJSON:
        print(
            json.dumps(
                format_scamper_json(
                    confidence,
                    destination_addr,
                    protocol.value,
                    min_ttl,
                    src_port,
                    dst_port,
                    wait,
                    start_time,
                    dminer.probes_sent,
                    dminer.all_replies(),
                )
            )
        )
    else:
        print(format_traceroute(dminer.all_replies()))
