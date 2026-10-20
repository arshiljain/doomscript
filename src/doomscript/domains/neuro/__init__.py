"""Computational Neuroscience & Spiking Neural Networks Domain Pack for DoomScript.

Enables native spoken-English Leaky Integrate-and-Fire neurons, STDP learning,
and Poisson spike train generation via 'use neuro'.
"""

from typing import List, Optional, Dict, Any
from doomscript.domains.base import (
    DomainContract,
    DomainRuntime,
    DomainIR,
    VerbSpec,
)
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.neuro.runtime import (
    LIFNeuron,
    IzhikevichNeuron,
    STDP,
    PoissonSpikeGenerator,
    SpikeAnalytics,
    neuro_create_lif,
    neuro_create_izhikevich,
    neuro_stdp_update,
    neuro_poisson_spikes,
    neuro_simulate_lif,
    TsodyksMarkramSynapse,
    FitzHughNagumoNeuron,
    WinnerTakeAllNetwork,
    HodgkinHuxleyNeuron,
    WilsonCowanNetwork,
    EEGBandpowerAnalyzer,
    PSTHAnalyzer,
    neuro_simulate_hodgkin_huxley,
    neuro_simulate_wilson_cowan,
    neuro_analyze_eeg_bands,
    neuro_compute_psth,
)
from doomscript.domains.neuro.parser import NeuroDomainParser
from doomscript.domains.neuro.exporter import NeuroASTExporter


class NeuroRuntime(DomainRuntime):
    """Runtime coordinator for neuroscience routines."""

    def execute_ir(self, ir: DomainIR, env: Dict[str, Any]) -> Any:
        return None


class NeuroDomain(DomainContract):
    """Domain contract for Computational Neuroscience & SNNs."""

    name = "neuro"
    aliases = ["neuroscience", "snn", "spiking", "lif", "stdp"]
    description = "Leaky Integrate-and-Fire neurons, Izhikevich dynamics, STDP synaptic plasticity, and Poisson spike trains"
    parser = NeuroDomainParser()
    runtime = NeuroRuntime()
    exporter = NeuroASTExporter()
    capabilities = ["lif", "izhikevich", "stdp", "poisson", "simulation"]
    optional_dependencies = {}

    verbs = [
        VerbSpec(
            pattern="create lif neuron into {target:ident}",
            description="Instantiates biological Leaky Integrate-and-Fire neuron",
        ),
        VerbSpec(
            pattern="generate poisson spikes with rate {rate:expr} duration {dur:expr} into {target:ident}",
            description="Generates stochastic Poisson point-process spike train",
        ),
        VerbSpec(
            pattern="apply stdp to weight {w:expr} with delta t {dt:expr} into {target:ident}",
            description="Updates synaptic weight using Spike-Timing-Dependent Plasticity",
        ),
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        if self.parser.parse_inspect(line, 0) is not None or self.parser.parse_operation(line, 0) is not None:
            return True
        s = line.strip().lower()
        return (
            s.startswith("create lif neuron ")
            or s.startswith("generate poisson spikes with ")
            or s.startswith("apply stdp to weight ")
            or s.startswith("simulate hodgkin huxley ")
            or s.startswith("simulate wilson cowan ")
            or s.startswith("analyze eeg bands ")
            or s.startswith("compute psth ")
        )

    def can_handle_block(self, header: str) -> bool:
        return False


NEURO_DOMAIN = NeuroDomain()
get_domain_registry().register(NEURO_DOMAIN)

__all__ = [
    "NeuroDomain",
    "NEURO_DOMAIN",
    "NeuroRuntime",
    "LIFNeuron",
    "IzhikevichNeuron",
    "STDP",
    "PoissonSpikeGenerator",
    "SpikeAnalytics",
    "neuro_create_lif",
    "neuro_create_izhikevich",
    "neuro_stdp_update",
    "neuro_poisson_spikes",
    "neuro_simulate_lif",
    "TsodyksMarkramSynapse",
    "FitzHughNagumoNeuron",
    "WinnerTakeAllNetwork",
    "HodgkinHuxleyNeuron",
    "WilsonCowanNetwork",
    "EEGBandpowerAnalyzer",
    "PSTHAnalyzer",
    "neuro_simulate_hodgkin_huxley",
    "neuro_simulate_wilson_cowan",
    "neuro_analyze_eeg_bands",
    "neuro_compute_psth",
]
