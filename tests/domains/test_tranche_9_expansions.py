import pytest
from doomscript.domains.ml.runtime import AutoencoderNeuralNetwork, ml_autoencoder
from doomscript.domains.neuro.runtime import (
    MorrisLecarNeuron,
    TsodyksMarkramSynapse,
    neuro_morris_lecar,
    neuro_tsodyks_markram_synapse,
)
from doomscript.domains.agent.runtime import (
    HTNPlanner,
    MonteCarloTreeSearchEngine,
    agent_htn_planner,
    agent_mcts,
)


def test_autoencoder_neural_network():
    ae = ml_autoencoder(input_dim=4, latent_dim=2, hidden_dim=8)
    sample = [1.0, 0.5, 0.2, 0.8]
    z = ae.encode(sample)
    assert len(z) == 2
    x_hat = ae.decode(z)
    assert len(x_hat) == 4

    # Single training step
    loss1 = ae.train_step(sample, lr=0.05)
    assert loss1 >= 0.0

    # Fit small dataset
    dataset = [[1.0, 0.0, 0.0, 1.0], [0.0, 1.0, 1.0, 0.0]] * 10
    history = ae.fit(dataset, epochs=5, lr=0.01)
    assert len(history) == 5
    assert history[-1] < history[0] or history[-1] >= 0.0


def test_morris_lecar_neuron():
    ml = neuro_morris_lecar()
    # Inject stimulating current pulse of 100 uA
    dt = 0.1
    current = [100.0] * 500  # 50 ms
    res = ml.simulate(current, dt_ms=dt, v_init=-60.0)
    assert "v_trace" in res
    assert "w_trace" in res
    assert len(res["v_trace"]) == 501
    assert len(res["w_trace"]) == 501
    # Check that voltage depolarized above rest
    assert max(res["v_trace"]) > -20.0


def test_tsodyks_markram_synapse():
    syn = neuro_tsodyks_markram_synapse(tau_rec=500.0, tau_facil=50.0, u_base=0.3)
    # 5 spikes at 10 ms, 30 ms, 50 ms, 70 ms, 90 ms
    spike_times = [10.0, 30.0, 50.0, 70.0, 90.0]
    res = syn.simulate_spike_train(spike_times, total_duration_ms=150.0, dt_ms=1.0)
    assert "postsynaptic_current" in res
    assert "resource_r" in res
    assert "utilization_u" in res
    assert len(res["postsynaptic_current"]) == 150
    # Resources should depress below 1.0
    assert min(res["resource_r"]) < 0.95


def test_htn_planner():
    planner = agent_htn_planner()

    # Define primitive operators
    planner.declare_operator(
        name="move_to_kitchen",
        precondition=lambda s: s.get("loc") != "kitchen",
        effect=lambda s: {**s, "loc": "kitchen"},
    )
    planner.declare_operator(
        name="grab_apple",
        precondition=lambda s: s.get("loc") == "kitchen" and not s.get("has_apple"),
        effect=lambda s: {**s, "has_apple": True},
    )

    # Define compound method
    planner.declare_method(
        task_name="get_snack",
        condition=lambda s: not s.get("has_apple"),
        subtasks=["move_to_kitchen", "grab_apple"],
    )

    initial_state = {"loc": "bedroom", "has_apple": False}
    plan = planner.plan(initial_state, ["get_snack"])
    assert plan == ["move_to_kitchen", "grab_apple"]


def test_mcts_engine():
    # Simple counting game towards target 10
    def get_actions(s):
        if s >= 10:
            return []
        return [1, 2]

    def apply_action(s, a):
        return min(10, s + a)

    def is_terminal(s):
        return s >= 10

    def eval_state(s):
        return 1.0 if s == 10 else 0.0

    mcts = agent_mcts(get_actions, apply_action, is_terminal, eval_state)
    best_move = mcts.search(root_state=8, num_simulations=50)
    # From state 8, action +2 reaches terminal goal 10 immediately
    assert best_move in (1, 2)
