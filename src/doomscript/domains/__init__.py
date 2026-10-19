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
]
