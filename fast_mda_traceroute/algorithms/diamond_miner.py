from collections import defaultdict
from ipaddress import IPv6Address
from random import shuffle
from typing import Dict, List

from diamond_miner.generators import probe_generator
from diamond_miner.mappers import SequentialFlowMapper
from diamond_miner.mda import stopping_point
from diamond_miner.typing import Probe
from more_itertools import flatten
from pycaracal import Reply

from fast_mda_traceroute.links import get_links_by_ttl, is_time_exceeded
from fast_mda_traceroute.typing import IPAddress


class DiamondMiner:
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
        self.current_round = 0
        self.probes_sent: Dict[int, int] = defaultdict(int)
        self.replies: Dict[int, List[Reply]] = {}

    def all_replies(self) -> List[Reply]:
        return list(flatten(self.replies.values()))

    def next_round(self, replies: List[Reply]) -> List[Probe]:
        self.current_round += 1
        self.replies[self.current_round] = replies

        if self.current_round > self.max_round:
            return []

        if self.current_round == 1:
            # TODO: Iteratively find the destination TTL (with a single flow?).
            max_flow = stopping_point(2, self.failure_probability)
            flows_by_ttl = {
                ttl: range(max_flow) for ttl in range(self.min_ttl, self.max_ttl + 1)
            }
        else:
            replies = [x for x in self.all_replies() if is_time_exceeded(x)]
            links_by_ttl = get_links_by_ttl(replies)
            flows_by_ttl = {}
            for ttl, links in links_by_ttl.items():
                # TODO: Full/Lite MDA.
                max_flow = stopping_point(len(links) + 1, self.failure_probability)
                flows_by_ttl[ttl] = range(self.probes_sent[ttl], max_flow)
            # TODO: Maximum over TTL (h-1, h); cf. Diamond-Miner paper `Proposition 1`.

        probes = []
        for ttl, flows in flows_by_ttl.items():
            probes_for_ttl = list(
                probe_generator(
                    [(str(self.destination), self.protocol)],
                    flow_ids=flows,
                    ttls=[ttl],
                    prefix_len_v4=32,
                    prefix_len_v6=128,
                    probe_src_port=self.src_port,
                    probe_dst_port=self.dst_port,
                    mapper_v4=self.mapper_v4,
                    mapper_v6=self.mapper_v6,
                )
            )
            self.probes_sent[ttl] += len(probes_for_ttl)
            probes.extend(probes_for_ttl)

        shuffle(probes)
        return probes
