from ipaddress import IPv6Address

from fast_mda_traceroute.links import (
    get_links_by_ttl,
    get_pairs_by_flow,
    get_replies_by_flow,
    get_replies_by_node_link,
)
from fast_mda_traceroute.test import MockReply


def test_get_replies_by_flow():
    replies_flow_1 = [
        MockReply.time_exceeded(1, "::9", 24000, 33434, 1, "::1"),
        MockReply.time_exceeded(1, "::9", 24000, 33434, 2, "::2"),
        MockReply.time_exceeded(1, "::9", 24000, 33434, 3, "::3"),
    ]
    replies_flow_2 = [
        MockReply.time_exceeded(1, "::9", 24001, 33434, 1, "::1"),
        MockReply.time_exceeded(1, "::9", 24001, 33434, 3, "::3"),
    ]
    assert get_replies_by_flow([*replies_flow_1, *replies_flow_2]) == {
        (1, IPv6Address("::9"), 24000, 33434): replies_flow_1,
        (1, IPv6Address("::9"), 24001, 33434): replies_flow_2,
    }


def test_get_pairs_by_flow():
    replies_flow_1 = [
        MockReply.time_exceeded(1, "::9", 24000, 33434, 1, "::1"),
        MockReply.time_exceeded(1, "::9", 24000, 33434, 2, "::2"),
        MockReply.time_exceeded(1, "::9", 24000, 33434, 3, "::3"),
    ]
    replies_flow_2 = [
        MockReply.time_exceeded(1, "::9", 24001, 33434, 1, "::1"),
        MockReply.time_exceeded(1, "::9", 24001, 33434, 3, "::3"),
    ]
    assert get_pairs_by_flow([*replies_flow_1, *replies_flow_2]) == {
        (1, IPv6Address("::9"), 24000, 33434): [
            (1, replies_flow_1[0], replies_flow_1[1]),
            (2, replies_flow_1[1], replies_flow_1[2]),
        ],
        (1, IPv6Address("::9"), 24001, 33434): [
            (1, replies_flow_2[0], None),
            (2, None, replies_flow_2[1]),
        ],
    }


def test_get_links_by_ttl():
    replies_flow_1 = [
        MockReply.time_exceeded(1, "::9", 24000, 33434, 1, "::1"),
        MockReply.time_exceeded(1, "::9", 24000, 33434, 2, "::2"),
        MockReply.time_exceeded(1, "::9", 24000, 33434, 3, "::3"),
    ]
    replies_flow_2 = [
        MockReply.time_exceeded(1, "::9", 24001, 33434, 1, "::1"),
        MockReply.time_exceeded(1, "::9", 24001, 33434, 3, "::3"),
    ]
    assert get_links_by_ttl([*replies_flow_1, *replies_flow_2]) == {
        1: {(1, IPv6Address("::1"), IPv6Address("::2")), (1, IPv6Address("::1"), None)},
        2: {(2, IPv6Address("::2"), IPv6Address("::3")), (2, None, IPv6Address("::3"))},
    }


def test_get_replies_by_node_link():
    replies_flow_1 = [
        MockReply.time_exceeded(1, "::9", 24000, 33434, 1, "::1"),
        MockReply.time_exceeded(1, "::9", 24000, 33434, 2, "::2"),
        MockReply.time_exceeded(1, "::9", 24000, 33434, 3, "::3"),
    ]
    replies_flow_2 = [
        MockReply.time_exceeded(1, "::9", 24001, 33434, 1, "::1"),
        MockReply.time_exceeded(1, "::9", 24001, 33434, 3, "::3"),
    ]
    assert get_replies_by_node_link([*replies_flow_1, *replies_flow_2]) == {
        IPv6Address("::1"): {IPv6Address("::2"): [replies_flow_1[1]], None: [None]},
        IPv6Address("::2"): {IPv6Address("::3"): [replies_flow_1[2]]},
        None: {IPv6Address("::3"): [replies_flow_2[1]]},
    }
