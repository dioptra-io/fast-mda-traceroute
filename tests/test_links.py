from fast_mda_traceroute.links import (
    get_links_by_ttl,
    get_pairs_by_flow,
    group_replies_by_flow,
)


def test_get_replies_by_flow(make_reply):
    replies_flow_1 = [
        make_reply(1, "::9", 24000, 33434, 1, "::1"),
        make_reply(1, "::9", 24000, 33434, 2, "::2"),
        make_reply(1, "::9", 24000, 33434, 3, "::3"),
    ]
    replies_flow_2 = [
        make_reply(1, "::9", 24001, 33434, 1, "::1"),
        make_reply(1, "::9", 24001, 33434, 3, "::3"),
    ]
    assert group_replies_by_flow([*replies_flow_1, *replies_flow_2]) == {
        (1, "::9", 24000, 33434): replies_flow_1,
        (1, "::9", 24001, 33434): replies_flow_2,
    }


def test_get_pairs_by_flow(make_reply):
    replies_flow_1 = [
        make_reply(1, "::9", 24000, 33434, 1, "::1"),
        make_reply(1, "::9", 24000, 33434, 2, "::2"),
        make_reply(1, "::9", 24000, 33434, 3, "::3"),
    ]
    replies_flow_2 = [
        make_reply(1, "::9", 24001, 33434, 1, "::1"),
        make_reply(1, "::9", 24001, 33434, 3, "::3"),
    ]
    assert get_pairs_by_flow([*replies_flow_1, *replies_flow_2]) == {
        (1, "::9", 24000, 33434): [
            (1, replies_flow_1[0], replies_flow_1[1]),
            (2, replies_flow_1[1], replies_flow_1[2]),
        ],
        (1, "::9", 24001, 33434): [
            (1, replies_flow_2[0], None),
            (2, None, replies_flow_2[1]),
        ],
    }


def test_get_links_by_ttl(make_reply):
    replies_flow_1 = [
        make_reply(1, "::9", 24000, 33434, 1, "::1"),
        make_reply(1, "::9", 24000, 33434, 2, "::2"),
        make_reply(1, "::9", 24000, 33434, 3, "::3"),
    ]
    replies_flow_2 = [
        make_reply(1, "::9", 24001, 33434, 1, "::1"),
        make_reply(1, "::9", 24001, 33434, 3, "::3"),
    ]
    assert get_links_by_ttl([*replies_flow_1, *replies_flow_2]) == {
        1: {(1, "::1", "::2"), (1, "::1", None)},
        2: {(2, "::2", "::3"), (2, None, "::3")},
    }
