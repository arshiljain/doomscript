import pytest
from doomscript.domains.registry import get_domain_registry
import doomscript.domains

def test_all_domains_have_verbs():
    reg = get_domain_registry()
    builtin_domains = [
        "data", "ml", "db", "net", "sim", "dsa", "viz", "research",
        "nlp", "geo", "opt", "agent", "image", "web", "audio",
        "finance", "graph", "office", "cloud"
    ]
    assert len(builtin_domains) == 19
    for name in builtin_domains:
        domain = reg.get_domain(name)
        assert domain is not None, f"Domain {name} not registered"
        assert hasattr(domain, "verbs"), f"Domain {name} missing verbs attribute"
        assert len(domain.verbs) > 0, f"Domain {name} has no declared verbs"
