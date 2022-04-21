import json
import logging
import socket
import sys
from datetime import datetime
from random import randint
from typing import List, Optional

import pycaracal
import typer
from pycaracal import Probe, Reply, experimental, utilities

from fast_mda_traceroute import __version__
from fast_mda_traceroute.algorithms import DiamondMiner
from fast_mda_traceroute.commands import paris_traceroute_command, scamper_command
from fast_mda_traceroute.dns import resolve
from fast_mda_traceroute.formats import (
    format_scamper_json,
    format_table,
    format_traceroute,
)
from fast_mda_traceroute.logger import logger
from fast_mda_traceroute.typing import (
    AddressFamily,
    DestinationType,
    EquivalentCommand,
    LogLevel,
    OutputFormat,
    Protocol,
)
from fast_mda_traceroute.utils import is_ipv4

app = typer.Typer()

eq_command_fns = {
    EquivalentCommand.ParisTraceroute: paris_traceroute_command,
    EquivalentCommand.Scamper: scamper_command,
}


def version_callback(value: bool):
    if value:
        print(f"fast-mda-traceroute {__version__}")
        raise typer.Exit()


@app.command()
def main(
    af: AddressFamily = typer.Option(
        AddressFamily.Any.value, help="IP version to use."
    ),
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
    _destination_type: DestinationType = typer.Option(
        DestinationType.Address.value,
        help="Whether to probe a single address, or the whole /24 or /64.",
    ),  # TODO: Implement.
    format: OutputFormat = typer.Option(
        OutputFormat.Table.value,
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
        1000,
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
    _version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=version_callback,
        help="Print program version.",
    ),
    destination: str = typer.Argument(..., help="Destination hostname or IP address."),
):
    # Configure Python logger
    logging.basicConfig(
        format="[%(asctime)s] %(message)s",
        level=log_level.value,
        stream=sys.stderr,
    )

    # Configure Caracal's C++ logger (spdlog)
    pycaracal.log_to_stderr()
    pycaracal.set_log_level(logging.getLevelName(log_level.value))
    pycaracal.set_log_format("[%Y-%m-%d %H:%M:%S,%e] %v")

    dst_addr = resolve(destination, af)[0]
    hostname = socket.gethostname()

    if is_ipv4(dst_addr):
        src_addr = utilities.source_ipv4_for(interface)
    else:
        src_addr = utilities.source_ipv6_for(interface)

    logger.info(
        "hostname=%s src_addr=%s dst_addr=%s interface=%s probing_rate=%d buffer_size=%d instance_id=%d integrity_check=%s version=%s",
        hostname,
        src_addr,
        dst_addr,
        interface,
        probing_rate,
        buffer_size,
        instance_id,
        integrity_check,
        __version__,
    )

    if print_command:
        eq_command_fn = eq_command_fns[print_command]
        eq_command = eq_command_fn(
            dst_addr,
            probing_rate,
            protocol,
            min_ttl,
            max_ttl,
            src_port,
            dst_port,
            wait,
        )
        print(eq_command)
        raise typer.Exit()

    prober = experimental.Prober(
        interface, probing_rate, buffer_size, instance_id, integrity_check
    )
    alg = DiamondMiner(
        dst_addr,
        min_ttl,
        max_ttl,
        src_port,
        dst_port,
        protocol.value,
        confidence,
        max_round,
    )

    start_time = datetime.now()
    last_replies: List[Reply] = []
    while True:
        probes = [Probe(*x) for x in alg.next_round(last_replies)]
        logger.info(
            "round=%d links_found=%d probes=%d expected_time=%.1fs",
            alg.current_round,
            len(alg.links),
            len(probes),
            len(probes) / probing_rate,
        )
        if not probes:
            break
        last_replies = prober.probe(probes, wait)
    stop_time = datetime.now()

    if format == OutputFormat.ScamperJSON:
        objs = format_scamper_json(
            confidence,
            probing_rate,
            hostname,
            src_addr,
            dst_addr,
            protocol,
            min_ttl,
            src_port,
            dst_port,
            wait,
            start_time,
            stop_time,
            alg.probes_sent,
            alg.time_exceeded_replies,
        )
        for obj in objs:
            print(json.dumps(obj))
    elif format == OutputFormat.Table:
        print(format_table(alg.time_exceeded_replies))
    else:
        print(format_traceroute(alg.time_exceeded_replies))
