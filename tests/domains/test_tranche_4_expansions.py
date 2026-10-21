"""Unit tests for Tranche 4 Domain Expansions (net, telecom, cloud)."""

import pytest
from doomscript.domains.net.runtime import (
    TCPTahoeRenoSimulator,
    RandomEarlyDetectionRED,
    BGP4PathVectorSimulator,
    net_tcp_simulate_reno,
    net_red_queue_simulate,
    net_bgp4_best_path,
)
from doomscript.domains.telecom.runtime import (
    LDPCBeliefPropagationDecoder,
    PolarCodeEncoderDecoder,
    MIMOSpatialMultiplexing,
    telecom_ldpc_decode,
    telecom_polar_encode_decode,
    telecom_mimo_detect_zf,
)
from doomscript.domains.cloud.runtime import (
    GossipMembershipProtocol,
    ChandyLamportSnapshot,
    cloud_gossip_simulate,
    cloud_chandy_lamport_snapshot,
)


def test_net_tcp_reno_congestion_control():
    """Verify TCP Reno AIMD dynamics and fast recovery."""
    res = net_tcp_simulate_reno(rtts=30, loss_rtts=[10])
    history = res.history_cwnd
    assert len(history) == 30
    # Before loss at RTT 10, cwnd must have been growing
    assert history[9] > history[1]
    # After loss at RTT 10, Reno halves cwnd to ssthresh
    assert history[10] < history[9]


def test_net_red_queue_management():
    """Verify RED drops packets above max threshold."""
    # Low queue lengths (< min_th = 5)
    low_queues = [1, 2, 2, 3, 2, 1]
    res_low = net_red_queue_simulate(low_queues, min_th=5.0, max_th=15.0)
    assert res_low.dropped_packets == 0

    # High queue lengths (> max_th = 10)
    high_queues = [15, 18, 20, 22, 25]
    res_high = net_red_queue_simulate(high_queues, min_th=5.0, max_th=10.0)
    assert res_high.dropped_packets > 0


def test_net_bgp4_best_path():
    """Verify BGP-4 selects shortest AS-path and filters AS loops."""
    routes = [
        {"prefix": "10.0.0.0/8", "as_path": [65001, 65002], "local_pref": 100, "router_id": "1.1.1.1"}, # Loop!
        {"prefix": "10.0.0.0/8", "as_path": [65002, 65003], "local_pref": 100, "router_id": "2.2.2.2"}, # len 2
        {"prefix": "10.0.0.0/8", "as_path": [65004], "local_pref": 100, "router_id": "3.3.3.3"},        # len 1 (best!)
    ]
    best = net_bgp4_best_path(routes, local_as=65001)
    assert best["router_id"] == "3.3.3.3"
    assert best["as_path"] == [65004]


def test_telecom_polar_code_and_mimo():
    """Verify 5G Polar Code encode/decode and 2x2 MIMO Zero-Forcing detection."""
    polar_res = telecom_polar_encode_decode([1, 0, 1, 1], n=8)
    assert polar_res.success is True
    assert len(polar_res.encoded_codeword) == 8

    # 2x2 MIMO Zero-Forcing
    # Transmitted symbols x = [2.0, 3.0]
    # H = [[1, 2], [3, 1]]
    # y = H * x = [1*2 + 2*3, 3*2 + 1*3] = [8.0, 9.0]
    H = [[1.0, 2.0], [3.0, 1.0]]
    y = [8.0, 9.0]
    mimo_res = telecom_mimo_detect_zf(H, y)
    assert mimo_res.detected_symbols[0] == pytest.approx(2.0, abs=0.01)
    assert mimo_res.detected_symbols[1] == pytest.approx(3.0, abs=0.01)


def test_cloud_gossip_and_snapshot():
    """Verify SWIM gossip failure detection and Chandy-Lamport snapshot."""
    res_gossip = cloud_gossip_simulate("node_1", ["node_2", "node_3"], rounds=5, failed_node="node_3")
    assert res_gossip.cluster_status["node_3"] in ("SUSPECT", "ALIVE")

    # Chandy-Lamport distributed snapshot
    nodes = ["proc_A", "proc_B", "proc_C"]
    channels = [
        {"from": "proc_A", "to": "proc_B", "messages": ["m1", "m2"]},
        {"from": "proc_B", "to": "proc_C", "messages": ["m3"]},
    ]
    snap = cloud_chandy_lamport_snapshot(nodes, channels, initiator="proc_A")
    assert snap.snapshot_consistent is True
    assert "proc_A" in snap.global_state
    assert len(snap.channel_states["proc_A->proc_B"]) == 2
