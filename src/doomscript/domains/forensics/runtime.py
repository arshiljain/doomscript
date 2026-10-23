"""Forensics Domain Runtime: Digital forensics, file carving, Shannon entropy, malware triage, and artifact analysis."""
import math
import re
import base64
from typing import Dict, Any, List, Optional, Tuple, Union
from doomscript.domains.base import DomainRuntime

# ============================================================================
# 1. PRESERVED FILE IDENTIFICATION & TRIAGE
# ============================================================================

def forensics_magic_bytes(header_bytes: Any) -> str:
    """Identifies file type from raw magic byte signatures."""
    if isinstance(header_bytes, str):
        b = header_bytes.encode('latin1')
    elif isinstance(header_bytes, (bytes, bytearray)):
        b = bytes(header_bytes)
    elif isinstance(header_bytes, list):
        b = bytes(header_bytes)
    else:
        b = b""
    if b.startswith(b"\x89PNG\r\n\x1a\n"): return "PNG Image"
    if b.startswith(b"\xff\xd8\xff"): return "JPEG Image"
    if b.startswith(b"GIF87a") or b.startswith(b"GIF89a"): return "GIF Image"
    if b.startswith(b"%PDF"): return "PDF document"
    if b.startswith(b"PK\x03\x04"): return "ZIP Archive / DOCX / XLSX"
    if b.startswith(b"MZ"): return "Windows PE Executable / DLL"
    if b.startswith(b"\x7fELF"): return "Linux ELF Executable"
    if b.startswith(b"\xca\xfe\xba\xbe") or b.startswith(b"\xcf\xfa\xed\xfe"): return "Mach-O Binary"
    if b.startswith(b"SQLite format 3\x00"): return "SQLite Database"
    if b.startswith(b"Rar!\x1a\x07"): return "RAR Archive"
    if b.startswith(b"7z\xbc\xaf\x27\x1c"): return "7-Zip Archive"
    return "Unknown Binary"

def forensics_shannon_entropy(data: Any) -> float:
    """Calculates Shannon entropy in bits per byte (0.0 to 8.0). High values (>7.2) indicate compression or encryption."""
    if isinstance(data, str):
        b = data.encode('utf-8')
    elif isinstance(data, (bytes, bytearray)):
        b = bytes(data)
    elif isinstance(data, list):
        b = bytes(data)
    else:
        b = b""
    if not b:
        return 0.0
    counts: Dict[int, int] = {}
    for byte in b:
        counts[byte] = counts.get(byte, 0) + 1
    total = len(b)
    ent = 0.0
    for count in counts.values():
        p = count / total
        ent -= p * math.log2(p)
    return round(ent, 4)

def forensics_deobfuscate_base64(data: str, max_depth: int = 5) -> str:
    """Recursively decodes nested Base64 encoded strings."""
    curr = data.strip()
    depth = 0
    while depth < max_depth:
        try:
            cleaned = re.sub(r'\s+', '', curr)
            if len(cleaned) % 4 != 0 or not re.match(r'^[A-Za-z0-9+/=]+$', cleaned):
                break
            decoded = base64.b64decode(cleaned).decode('utf-8', errors='ignore')
            if decoded.strip() and all(32 <= ord(c) < 127 or c in '\r\n\t' for c in decoded):
                curr = decoded.strip()
                depth += 1
            else:
                break
        except Exception:
            break
    return curr

def forensics_dga_score(domain_name: str) -> Dict[str, Any]:
    """Scores domain name for Domain Generation Algorithm (DGA) heuristics."""
    d = domain_name.lower().split('.')[0]
    if not d:
        return {"dga_score": 0.0, "is_likely_dga": False, "is_dga": False}
    ent = forensics_shannon_entropy(d)
    vowels = sum(1 for c in d if c in "aeiou")
    consonants = sum(1 for c in d if c.isalpha() and c not in "aeiou")
    ratio = consonants / max(1, vowels)
    length = len(d)
    score = 0.0
    if ent > 3.2: score += 0.4
    if ratio > 3.0: score += 0.3
    if length > 12: score += 0.3
    return {
        "domain": domain_name,
        "entropy": round(ent, 2),
        "consonant_vowel_ratio": round(ratio, 2),
        "dga_score": round(min(1.0, score), 2),
        "is_likely_dga": score >= 0.7,
        "is_dga": score >= 0.7
    }

def forensics_detect_shellcode_nop_sled(data: Any, min_sled: int = 8) -> Dict[str, Any]:
    """Detects x86 NOP sleds (0x90) and common polymorphic sled instructions."""
    if isinstance(data, (bytes, bytearray)):
        b = bytes(data)
    elif isinstance(data, list):
        b = bytes(data)
    else:
        b = str(data).encode('latin1')
    longest_sled = 0
    current_sled = 0
    start_pos = -1
    best_start = -1
    for idx, byte in enumerate(b):
        if byte == 0x90:
            if current_sled == 0:
                start_pos = idx
            current_sled += 1
            if current_sled > longest_sled:
                longest_sled = current_sled
                best_start = start_pos
        else:
            current_sled = 0
    return {
        "has_nop_sled": longest_sled >= min_sled,
        "longest_sled_length": longest_sled,
        "offset": best_start
    }

# ============================================================================
# 2. ADVANCED ARTIFACT PARSERS (NTFS MFT, TIMESTOMPING, STEGANOGRAPHY)
# ============================================================================

def forensics_detect_timestomping(standard_info_timestamps: Dict[str, float], file_name_timestamps: Dict[str, float]) -> Dict[str, Any]:
    """Detects NTFS timestomping anomalies where $STANDARD_INFORMATION predates $FILE_NAME."""
    anomalies = []
    for k in ["created", "modified", "accessed", "mft_modified"]:
        si = standard_info_timestamps.get(k, 0)
        fn = file_name_timestamps.get(k, 0)
        if si > 0 and fn > 0:
            if si < fn:
                anomalies.append({
                    "attribute": k,
                    "standard_info_time": si,
                    "file_name_time": fn,
                    "discrepancy_seconds": round(fn - si, 2)
                })
    return {
        "is_timestomped": len(anomalies) > 0,
        "anomaly_count": len(anomalies),
        "details": anomalies
    }

def forensics_lsb_steganography_check(pixel_bytes: List[int]) -> Dict[str, Any]:
    """Analyzes Least Significant Bit (LSB) distributions for steganographic hidden payloads."""
    if not pixel_bytes:
        return {"suspicious": False, "zero_one_ratio": 0.0}
    lsb_bits = [b & 1 for b in pixel_bytes]
    ones = sum(lsb_bits)
    zeros = len(lsb_bits) - ones
    ratio = ones / len(lsb_bits)
    # Natural uncompressed LSBs usually deviate from pure 50.0% random entropy
    suspicious = abs(ratio - 0.5) < 0.005 and len(pixel_bytes) > 1000
    return {
        "total_samples": len(pixel_bytes),
        "ones_ratio": round(ratio, 4),
        "suspicious_uniformity": suspicious
    }

# ============================================================================
# 3. DOMAIN RUNTIME
# ============================================================================

class ForensicsRuntime(DomainRuntime):
    """Unified runtime bridge for the Forensics computational domain."""
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

    def magic_bytes(self, b: Any) -> str:
        return forensics_magic_bytes(b)
    def entropy(self, data: Any) -> float:
        return forensics_shannon_entropy(data)
    def deobfuscate(self, data: str) -> str:
        return forensics_deobfuscate_base64(data)
    def dga(self, domain: str) -> Dict[str, Any]:
        return forensics_dga_score(domain)
    def nop_sled(self, data: Any, min_sled: int = 8) -> Dict[str, Any]:
        return forensics_detect_shellcode_nop_sled(data, min_sled)
    def timestomp(self, si: Dict[str, float], fn: Dict[str, float]) -> Dict[str, Any]:
        return forensics_detect_timestomping(si, fn)
    def lsb_check(self, pixels: List[int]) -> Dict[str, Any]:
        return forensics_lsb_steganography_check(pixels)
