"""DoomScript Domain Extensions System."""

from doomscript.domains.base import (
    DomainContract,
    DomainParser,
    DomainIR,
    DomainRuntime,
    DomainASTExporter,
)
from doomscript.domains.registry import DomainRegistry, get_domain_registry
from doomscript.domains.data import DATA_DOMAIN
from doomscript.domains.ml import ML_DOMAIN
from doomscript.domains.db import DB_DOMAIN
from doomscript.domains.net import NET_DOMAIN
from doomscript.domains.sim import SIM_DOMAIN
from doomscript.domains.dsa import DSA_DOMAIN
from doomscript.domains.viz import VIZ_DOMAIN
from doomscript.domains.research import RESEARCH_DOMAIN
from doomscript.domains.nlp import NLP_DOMAIN
from doomscript.domains.geo import GEO_DOMAIN
from doomscript.domains.opt import OPT_DOMAIN
from doomscript.domains.agent import AGENT_DOMAIN
from doomscript.domains.image import IMAGE_DOMAIN
from doomscript.domains.web import WEB_DOMAIN
from doomscript.domains.audio import AUDIO_DOMAIN
from doomscript.domains.finance import FINANCE_DOMAIN
from doomscript.domains.graph import GRAPH_DOMAIN
from doomscript.domains.office import OFFICE_DOMAIN
from doomscript.domains.cloud import CLOUD_DOMAIN
from doomscript.domains.bio import BIO_DOMAIN
from doomscript.domains.physics import PHYSICS_DOMAIN
from doomscript.domains.sec import SEC_DOMAIN
from doomscript.domains.game import GAME_DOMAIN
from doomscript.domains.quantum import QUANTUM_DOMAIN
from doomscript.domains.circuit import CIRCUIT_DOMAIN
from doomscript.domains.chain import CHAIN_DOMAIN
from doomscript.domains.math3d import MATH3D_DOMAIN
from doomscript.domains.compiler import COMPILER_DOMAIN
from doomscript.domains.robotics import ROBOTICS_DOMAIN
from doomscript.domains.signals import SIGNALS_DOMAIN
from doomscript.domains.astronomy import ASTRONOMY_DOMAIN
from doomscript.domains.chem import CHEM_DOMAIN
from doomscript.domains.compression import COMPRESSION_DOMAIN
from doomscript.domains.time_series import TIME_SERIES_DOMAIN
from doomscript.domains.symbolic import SYMBOLIC_DOMAIN
from doomscript.domains.graphics import GRAPHICS_DOMAIN
from doomscript.domains.telecom import TELECOM_DOMAIN
from doomscript.domains.neuro import NEURO_DOMAIN
from doomscript.domains.automata import AUTOMATA_DOMAIN
from doomscript.domains.metrics import METRICS_DOMAIN
from doomscript.domains.spatial_audio import SPATIAL_AUDIO_DOMAIN
from doomscript.domains.genai import GENAI_DOMAIN
from doomscript.domains.cache import CACHE_DOMAIN
from doomscript.domains.queue import QUEUE_DOMAIN
from doomscript.domains.crypto_zk import CRYPTO_ZK_DOMAIN
from doomscript.domains.climate import CLIMATE_DOMAIN
from doomscript.domains.genomics import GENOMICS_DOMAIN
from doomscript.domains.hydrology import HYDROLOGY_DOMAIN
from doomscript.domains.materials import MATERIALS_DOMAIN
from doomscript.domains.aerospace import AEROSPACE_DOMAIN
from doomscript.domains.control import CONTROL_DOMAIN
from doomscript.domains.ecology import ECOLOGY_DOMAIN
from doomscript.domains.epidemiology import EPIDEMIOLOGY_DOMAIN
from doomscript.domains.logistics import LOGISTICS_DOMAIN
from doomscript.domains.forensics import FORENSICS_DOMAIN
from doomscript.domains.microecon import MICROECON_DOMAIN
from doomscript.domains.risk import RISK_DOMAIN
from doomscript.domains.social import SOCIAL_DOMAIN
from doomscript.domains.linguistics import LINGUISTICS_DOMAIN
from doomscript.domains.geophysics import GEOPHYSICS_DOMAIN
from doomscript.domains.synthetic_bio import SYNTHETIC_BIO_DOMAIN
from doomscript.domains.thermodynamics import THERMODYNAMICS_DOMAIN
from doomscript.domains.optics import OPTICS_DOMAIN
from doomscript.domains.acoustics import ACOUSTICS_DOMAIN
from doomscript.domains.oceanography import OCEANOGRAPHY_DOMAIN
from doomscript.domains.astrophysics import ASTROPHYSICS_DOMAIN
from doomscript.domains.petroleum import PETROLEUM_DOMAIN
from doomscript.domains.metallurgy import METALLURGY_DOMAIN
from doomscript.domains.ergonomics import ERGONOMICS_DOMAIN
from doomscript.domains.biomechanics import BIOMECHANICS_DOMAIN
from doomscript.domains.actuarial import ACTUARIAL_DOMAIN
from doomscript.domains.pharmacology import PHARMACOLOGY_DOMAIN
from doomscript.domains.electromagnetics import ELECTROMAGNETICS_DOMAIN
from doomscript.domains.combustion import COMBUSTION_DOMAIN
from doomscript.domains.nuclear import NUCLEAR_DOMAIN
from doomscript.domains.cartography import CARTOGRAPHY_DOMAIN
from doomscript.domains.chronometry import CHRONOMETRY_DOMAIN
from doomscript.domains.agronomy import AGRONOMY_DOMAIN
from doomscript.domains.crystallography import CRYSTALLOGRAPHY_DOMAIN
from doomscript.domains.aviation import AVIATION_DOMAIN
from doomscript.domains.structural import STRUCTURAL_DOMAIN

__all__ = [
    "DomainContract",
    "DomainParser",
    "DomainIR",
    "DomainRuntime",
    "DomainASTExporter",
    "DomainRegistry",
    "get_domain_registry",
    "DATA_DOMAIN",
    "ML_DOMAIN",
    "DB_DOMAIN",
    "NET_DOMAIN",
    "SIM_DOMAIN",
    "DSA_DOMAIN",
    "VIZ_DOMAIN",
    "RESEARCH_DOMAIN",
    "NLP_DOMAIN",
    "GEO_DOMAIN",
    "OPT_DOMAIN",
    "AGENT_DOMAIN",
    "IMAGE_DOMAIN",
    "WEB_DOMAIN",
    "AUDIO_DOMAIN",
    "FINANCE_DOMAIN",
    "GRAPH_DOMAIN",
    "OFFICE_DOMAIN",
    "CLOUD_DOMAIN",
    "BIO_DOMAIN",
    "PHYSICS_DOMAIN",
    "SEC_DOMAIN",
    "GAME_DOMAIN",
    "QUANTUM_DOMAIN",
    "CIRCUIT_DOMAIN",
    "CHAIN_DOMAIN",
    "MATH3D_DOMAIN",
    "COMPILER_DOMAIN",
    "ROBOTICS_DOMAIN",
    "SIGNALS_DOMAIN",
    "ASTRONOMY_DOMAIN",
    "CHEM_DOMAIN",
    "COMPRESSION_DOMAIN",
    "TIME_SERIES_DOMAIN",
    "SYMBOLIC_DOMAIN",
    "GRAPHICS_DOMAIN",
    "TELECOM_DOMAIN",
    "NEURO_DOMAIN",
    "AUTOMATA_DOMAIN",
    "METRICS_DOMAIN",
    "SPATIAL_AUDIO_DOMAIN",
    "GENAI_DOMAIN",
    "CACHE_DOMAIN",
    "QUEUE_DOMAIN",
    "CRYPTO_ZK_DOMAIN",
    "CLIMATE_DOMAIN",
    "GENOMICS_DOMAIN",
    "HYDROLOGY_DOMAIN",
    "MATERIALS_DOMAIN",
    "AEROSPACE_DOMAIN",
    "CONTROL_DOMAIN",
    "ECOLOGY_DOMAIN",
    "EPIDEMIOLOGY_DOMAIN",
    "LOGISTICS_DOMAIN",
    "FORENSICS_DOMAIN",
    "MICROECON_DOMAIN",
    "RISK_DOMAIN",
    "SOCIAL_DOMAIN",
    "LINGUISTICS_DOMAIN",
    "GEOPHYSICS_DOMAIN",
    "SYNTHETIC_BIO_DOMAIN",
    "THERMODYNAMICS_DOMAIN",
    "OPTICS_DOMAIN",
    "ACOUSTICS_DOMAIN",
    "OCEANOGRAPHY_DOMAIN",
    "ASTROPHYSICS_DOMAIN",
    "PETROLEUM_DOMAIN",
    "METALLURGY_DOMAIN",
    "ERGONOMICS_DOMAIN",
    "BIOMECHANICS_DOMAIN",
    "ACTUARIAL_DOMAIN",
    "PHARMACOLOGY_DOMAIN",
    "ELECTROMAGNETICS_DOMAIN",
    "COMBUSTION_DOMAIN",
    "NUCLEAR_DOMAIN",
    "CARTOGRAPHY_DOMAIN",
    "CHRONOMETRY_DOMAIN",
    "AGRONOMY_DOMAIN",
    "CRYSTALLOGRAPHY_DOMAIN",
    "AVIATION_DOMAIN",
    "STRUCTURAL_DOMAIN",
]
