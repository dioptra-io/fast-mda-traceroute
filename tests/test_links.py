from fast_mda_traceroute.links import (
    get_links_by_ttl,
    get_pairs_by_flow,
    get_replies_by_flow,
    get_replies_by_ttl,
    get_scamper_links,
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
    assert get_replies_by_flow([*replies_flow_1, *replies_flow_2]) == {
        (1, "::9", 24000, 33434): replies_flow_1,
        (1, "::9", 24001, 33434): replies_flow_2,
    }


def test_get_replies_by_ttl(make_reply):
    replies_ttl_1 = [
        make_reply(1, "::9", 24000, 33434, 1, "::1"),
        make_reply(1, "::9", 24001, 33434, 1, "::1"),
    ]
    replies_ttl_2 = [
        make_reply(1, "::9", 24000, 33434, 2, "::2"),
    ]
    replies_ttl_3 = [
        make_reply(1, "::9", 24000, 33434, 3, "::3"),
        make_reply(1, "::9", 24001, 33434, 3, "::3"),
    ]
    assert get_replies_by_ttl([*replies_ttl_1, *replies_ttl_2, *replies_ttl_3]) == {
        1: replies_ttl_1,
        2: replies_ttl_2,
        3: replies_ttl_3,
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


def test_get_scamper_links(make_reply):
    replies_flow_1 = [
        make_reply(1, "::9", 24000, 33434, 1, "::1"),
        make_reply(1, "::9", 24000, 33434, 2, "::2"),
        make_reply(1, "::9", 24000, 33434, 3, "::3"),
    ]
    replies_flow_2 = [
        make_reply(1, "::9", 24001, 33434, 1, "::1"),
        make_reply(1, "::9", 24001, 33434, 3, "::3"),
    ]
    assert get_scamper_links([*replies_flow_1, *replies_flow_2]) == {
        "::1": {
            2: {"::2": [replies_flow_1[1]], None: [None]},
            3: {"::3": [replies_flow_2[1]]},
        },
        "::2": {3: {"::3": [replies_flow_1[2]]}},
    }
