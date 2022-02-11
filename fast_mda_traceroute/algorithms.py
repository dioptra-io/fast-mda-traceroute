from collections import defaultdict
from ipaddress import IPv6Address

from diamond_miner.generators import probe_generator_by_flow
from diamond_miner.mappers import SequentialFlowMapper
from diamond_miner.mda import stopping_point
from more_itertools import flatten

from fast_mda_traceroute.links import filter_replies, get_links_by_ttl
from fast_mda_traceroute.typing import IPAddress


class DiamondMinerLite:
    """A standalone, in-memory, version of Diamond-Miner."""

    def __init__(
        self,
        destination: IPAddress,
        min_ttl: int,
        max_ttl: int,
        src_port: int,
        dst_port: int,
        protocol: str,
        confidence: int,
        max_round: int,
    ):
        if protocol == "icmp" and isinstance(destination, IPv6Address):
            protocol = "icmp6"
        self.failure_probability = 1 - (confidence / 100)
        self.destination = destination
        self.min_ttl = min_ttl
        self.max_ttl = max_ttl
        self.src_port = src_port
        self.dst_port = dst_port
        self.protocol = protocol
        self.mapper_v4 = SequentialFlowMapper(prefix_size=1)
        self.mapper_v6 = SequentialFlowMapper(prefix_size=1)
        self.max_round = max_round
        # Diamond-Miner state
        self.round = 0
        self.probes = defaultdict(int)
        self.replies = {}

    def next_round(self, replies):
        self.round += 1
        self.replies[self.round] = replies

        if self.round > self.max_round:
            return []

        if self.round == 1:
            n_flows = stopping_point(2, self.failure_probability)
            prefix = (
                str(self.destination),
                self.protocol,
                range(self.min_ttl, self.max_ttl + 1),
            )
            # TODO: Refactor...
            for ttl in range(self.min_ttl, self.max_ttl + 1):
                self.probes[ttl] += n_flows
            return list(
                probe_generator_by_flow(
                    [prefix],
                    flow_ids=range(n_flows),
                    prefix_len_v4=32,
                    prefix_len_v6=128,
                    probe_src_port=self.src_port,
                    probe_dst_port=self.dst_port,
                    mapper_v4=self.mapper_v4,
                    mapper_v6=self.mapper_v6,
                )
            )

        replies = set(filter_replies(flatten(self.replies.values())))
        links_by_ttl = get_links_by_ttl(replies)
        probes = []
        for ttl, links in links_by_ttl.items():
            first_flow = self.probes[ttl]
            # TODO: Max over ttl, ttl+1 (cf. paper).
            last_flow = stopping_point(len(links) + 1, self.failure_probability)
            self.probes[ttl] = last_flow
            probes.extend(
                list(
                    probe_generator_by_flow(
                        [(str(self.destination), self.protocol, [ttl])],
                        flow_ids=range(first_flow, last_flow),
                        prefix_len_v4=32,
                        prefix_len_v6=128,
                        probe_src_port=self.src_port,
                        probe_dst_port=self.dst_port,
                        mapper_v4=self.mapper_v4,
                        mapper_v6=self.mapper_v6,
                    )
                )
            )
        return probes
