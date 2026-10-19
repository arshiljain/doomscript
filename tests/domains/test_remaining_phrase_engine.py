import pytest
from doomscript.domains.registry import get_domain_registry
import doomscript.domains

def test_all_domains_have_verbs():
    reg = get_domain_registry()
    assert len(reg._domains) >= 18
    for name, domain in reg._domains.items():
        assert hasattr(domain, "verbs"), f"Domain {name} missing verbs attribute"
        assert len(domain.verbs) > 0, f"Domain {name} has no declared verbs"
