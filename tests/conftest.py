import pytest
from pycaracal import Reply


@pytest.fixture
def make_reply():
    def _make_reply(
        probe_protocol: int,
        probe_dst_addr: str,
        probe_src_port: int,
        probe_dst_port: int,
        probe_ttl: int,
        reply_src_addr: str,
    ):
        reply = Reply()
        reply.probe_protocol = probe_protocol
        reply.probe_dst_addr = probe_dst_addr
        reply.probe_src_port = probe_src_port
        reply.probe_dst_port = probe_dst_port
        reply.probe_ttl = probe_ttl
        reply.reply_src_addr = reply_src_addr
        return reply

    return _make_reply
