"""Digital Forensics Runtime: Magic byte headers, Shannon entropy, Base64 deobfuscation, DGA detection, and NOP sled scans."""
import math
import base64
import re
from typing import Dict, Any, Optional

FILE_SIGNATURES = {
    b"\x89PNG\r\n\x1a\n": "PNG image",
    b"\xff\xd8\xff": "JPEG image",
    b"%PDF": "PDF document",
    b"PK\x03\x04": "ZIP/Office archive",
    b"\x7fELF": "ELF executable",
    b"MZ": "PE/Windows executable",
    b"GIF87a": "GIF image",
    b"GIF89a": "GIF image"
}

def forensics_magic_bytes(header_bytes: Any) -> str:
    """Identifies file type from leading bytes header."""
    if isinstance(header_bytes, str):
        header_bytes = header_bytes.encode('latin1')
    for magic, desc in FILE_SIGNATURES.items():
        if header_bytes.startswith(magic):
            return desc
    return "Unknown binary format"

def forensics_shannon_entropy(data: Any) -> float:
    """Calculates Shannon Entropy (0.0 to 8.0) of a byte stream to detect encryption/compression."""
    if isinstance(data, str):
        data = data.encode('utf-8')
    if not data:
        return 0.0
    freq = [0] * 256
    for b in data:
        freq[b] += 1
    total = len(data)
    entropy = 0.0
    for count in freq:
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)
    return round(entropy, 4)

def forensics_deobfuscate_base64(data: str, max_depth: int = 5) -> str:
    """Recursively decodes nested base64 layers until plain text is recovered."""
    curr = str(data).strip()
    for _ in range(max_depth):
        try:
            decoded = base64.b64decode(curr, validate=True).decode('utf-8', errors='ignore')
            if decoded and decoded != curr:
                curr = decoded
            else:
                break
        except Exception:
            break
    return curr

def forensics_dga_score(domain_name: str) -> Dict[str, Any]:
    """Scores a domain name for DGA (Domain Generation Algorithm) malware characteristics."""
    d = str(domain_name).split(".")[0].lower()
    if not d:
        return {"dga_score": 0.0, "is_dga": False}
    # Calculate vowel ratio
    vowels = sum(1 for c in d if c in "aeiou")
    vowel_ratio = vowels / len(d)
    # Consecutive consonants
    max_consonants = max(len(s) for s in re.findall(r"[^aeiou\d]+", d)) if re.findall(r"[^aeiou\d]+", d) else 0
    # Shannon entropy of characters
    char_freq = {}
    for c in d:
        char_freq[c] = char_freq.get(c, 0) + 1
    ent = -sum((cnt / len(d)) * math.log2(cnt / len(d)) for cnt in char_freq.values())
    is_dga = ent > 3.2 or max_consonants >= 5 or vowel_ratio < 0.15
    score = min(1.0, (ent / 4.0) * 0.5 + (max_consonants / 6.0) * 0.5)
    return {"dga_score": round(score, 2), "is_dga": is_dga, "entropy": round(ent, 2), "max_consonants": max_consonants}

def forensics_detect_shellcode_nop_sled(data: Any, min_sled: int = 8) -> Dict[str, Any]:
    """Detects x86 NOP sled (0x90 sequence) landing pads."""
    if isinstance(data, str):
        b = data.encode('latin1')
    else:
        b = bytes(data)
    nop = b"\x90" * int(min_sled)
    idx = b.find(nop)
    return {"has_nop_sled": idx != -1, "offset": idx if idx != -1 else None}
