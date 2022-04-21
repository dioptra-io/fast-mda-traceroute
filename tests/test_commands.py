from fast_mda_traceroute.commands import (
    get_paris_traceroute_command,
    get_scamper_command,
)
from fast_mda_traceroute.typing import Protocol


def test_get_paris_traceroute_command():
    expected = "paris-traceroute --algorithm mda --src-port 24000 --dst-port 33434 --icmp --first 2 --max-hops 32 -q 1 -w 1 8.8.8.8"
    actual = get_paris_traceroute_command(
        "8.8.8.8", 100, Protocol.ICMP, 2, 32, 24000, 33434, 1000
    )
    assert actual == expected


def test_get_paris_scamper_command():
    expected = 'scamper -p 100 -O json -I "tracelb -P icmp-echo -s 24000 -d 33434 -f 2 -q 1 -w 1 8.8.8.8"'
    actual = get_scamper_command(
        "8.8.8.8", 100, Protocol.ICMP, 2, 32, 24000, 33434, 1000
    )
    assert actual == expected
