"""Digital Forensics Runtime: Magic byte signature matching, Shannon entropy, and base64 deobfuscation."""
import math
import base64
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

def forensics_deobfuscate_base64(text: str, max_depth: int = 5) -> str:
    """Recursively decodes nested base64 encoded strings."""
    curr = str(text).strip()
    depth = 0
    while depth < max_depth:
        try:
            decoded = base64.b64decode(curr, validate=True).decode('utf-8')
            if decoded.isprintable() and len(decoded) > 0:
                curr = decoded
                depth += 1
            else:
                break
        except Exception:
            break
    return curr
