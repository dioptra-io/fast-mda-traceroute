from collections import defaultdict
from math import ceil
from random import shuffle
from typing import Dict, List, Set

from diamond_miner.generators import probe_generator
from diamond_miner.mappers import SequentialFlowMapper
from diamond_miner.typing import Probe
from more_itertools import flatten
from pycaracal import Reply

from fast_mda_traceroute.algorithms.utils.stopping_point import stopping_point
from fast_mda_traceroute.links import get_links_by_ttl
from fast_mda_traceroute.typing import Link
from fast_mda_traceroute.utils import is_ipv4



class DiamondMiner:
    """A standalone, in-memory, version of Diamond-Miner."""

    def __init__(
        self,
        dst_addr: str,
        min_ttl: int,
        max_ttl: int,
        src_port: int,
        dst_port: int,
        protocol: str,
        confidence: float,
        max_round: int,
    ):
        if protocol == "icmp" and not is_ipv4(dst_addr):
            protocol = "icmp6"
        self.failure_probability = 1.0 - (confidence / 100.0)
        self.dst_addr = dst_addr
        self.min_ttl = min_ttl
        self.max_ttl = max_ttl
        self.src_port = src_port
        self.dst_port = dst_port
        self.protocol = protocol
        # We only use a prefix_size of 1 for direct
        # point-to-point paths
        self.mapper_v4 = SequentialFlowMapper(prefix_size=1)
        self.mapper_v6 = SequentialFlowMapper(prefix_size=1)
        self.max_round = max_round
        # Diamond-Miner state
        self.current_round = 0
        self.probes_sent: Dict[int, int] = defaultdict(int)
        self.replies_by_round: Dict[int, List[Reply]] = {}
        self.n_unresolved = [0 for _ in range(self.max_ttl + 1)]

    @property
    def links_by_ttl(self) -> Dict[int, Set[Link]]:
        return get_links_by_ttl(self.time_exceeded_replies)

    @property
    def links(self) -> Set[Link]:
        return set(flatten(self.links_by_ttl.values()))

    @property
    def replies(self) -> List[Reply]:
        return list(flatten(self.replies_by_round.values()))

    @property
    def time_exceeded_replies(self) -> List[Reply]:
        return [x for x in self.replies if x.time_exceeded]

    @property
    def destination_unreachable_replies(self) -> List[Reply]:
        return [x for x in self.replies if x.destination_unreachable]

    @property
    def echo_replies(self) -> List[Reply]:
        return [x for x in self.replies if x.echo_reply]

    def nodes_distribution_at_ttl(self, nodes: List[str], ttl: int) -> Dict[str, float]:
        # a routine to fetch the number of replies from a given node at a given TTL
        # NOTE: a node may appear at multiple TTLs
        def node_replies(node, ttl):
            return len([
                r
                for r in self.time_exceeded_replies
                if r.reply_src_addr == node and r.probe_ttl == ttl
            ]
            )

        # total number of observations of links reaching nodes at the current ttl.
        # since links are stored with the 'near_ttl',
        # we need to fetch them at ttl-1
        all_replies = len(self.links_by_ttl.get(ttl - 1, []))

        if all_replies:
            # compute the probability distribution of nodes at the current ttl
            link_dist = {node: node_replies(node, ttl) / all_replies for node in nodes}
        else:
            # if we did not observe links at the previous ttl
            # we won't apply weights to the n_k afterwards
            link_dist = {node: 1.0 for node in nodes}

        return link_dist

    def unresolved_nodes_at_ttl(self, ttl: int) -> List[str]:
        # returns the list of unresolved nodes at a given TTL
        # a node is said to be unresolved if not enough probes
        # have observed the outgoing links of this node.
        # This threshold is given by the stopping_point routine.
        # Resolved vertices correspond to nodes where all
        # outgoing load balanced links have been discovered
        # with high probability toward the destination.
        unresolved = []
        weighted_thresholds = []

        # for every discovered node at this TTL (non None)
        nodes_at_ttl = set(filter(bool, (x[1] for x in self.links_by_ttl[ttl])))

        # fetch the distribution of the nodes at this TTL.
        # this is important to determine what percentage of probes
        # sent to this TTL will eventually reach each specific node.
        link_dist = self.nodes_distribution_at_ttl(nodes_at_ttl, ttl)

        for node in nodes_at_ttl:
            # number of unique nodes at the next TTL that share a link with the node
            n_successors = len(
                set(
                    [
                        x[2]
                        for x in self.links_by_ttl[ttl]
                        if x[1] == node and x[2] is not None
                    ]
                )
            )

            # the minimum number of probes to send to confirm we got all successors
            # We try to dismiss the hypothesis that there are more successors than we observed
            n_k = stopping_point(n_successors + 1, self.failure_probability)

            # number of outgoing probes that went through the node
            n_probes = len([x for x in self.links_by_ttl[ttl] if x[1] == node])

            # if we have not sent enough probes for this node
            if n_probes < n_k:

                # mark the node as unresolved
                unresolved.append(node)

                # we store the total number of probes to send to get confirmation:
                # it is the threshold n_k weighted by how difficult it is to reach
                # this node, i.e. the distribution of probes that reach this node
                weighted_thresholds.append(n_k / link_dist[node])

        # we store the number of unresolved nodes at each TTL for logging purposes
        self.n_unresolved[ttl] = len(unresolved)

        return unresolved, ceil(max(weighted_thresholds, default=0))

    def next_round(self, replies: List[Reply]) -> List[Probe]:
        self.current_round += 1

        self.replies_by_round[self.current_round] = replies

        if self.current_round > self.max_round:
            return []

        max_flows_by_ttl = defaultdict(int)

        if self.current_round == 1:
            # NOTE: we cannot reliably infer the destination TTL because it may not be unique.

            # we could send only one probe per TTL, but that would not resolve any node.
            # max_flow = 1
            max_flow = stopping_point(2, self.failure_probability)
            max_flows_by_ttl = {
                ttl: max_flow for ttl in range(self.min_ttl, self.max_ttl + 1)
            }
        else:
            max_flows_by_ttl = {
                ttl: self.unresolved_nodes_at_ttl(ttl)[1]
                for ttl in range(self.min_ttl, self.max_ttl + 1)
            }

        # See Proposition 1 in the original Diamond Miner paper.
        # The max flow for a TTL is the one computed for unresolved nodes at this TTL
        # or the one computed at the previous TTL to traverse the previous TTL:
        # we take the max of both values.

        def combined_max_flow(ttl):
            return max(
                max_flows_by_ttl[ttl], max_flows_by_ttl.get(ttl - 1, 0)
            )
        flows_by_ttl = {
            ttl: range(self.probes_sent[ttl], combined_max_flow(ttl))
            for ttl in range(self.min_ttl, self.max_ttl + 1)
        }

        probes = []
        for ttl, flows in flows_by_ttl.items():
            probes_for_ttl = list(
                probe_generator(
                    [(self.dst_addr, self.protocol)],
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
