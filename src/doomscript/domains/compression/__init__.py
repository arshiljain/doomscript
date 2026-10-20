"""Lossless Compression & Information Theory Domain Pack for DoomScript.

Enables native spoken-English Huffman, LZW, LZ77, RLE compression, and Shannon entropy
via 'use compression'.
"""

from typing import List, Optional, Dict, Any
from doomscript.domains.base import (
    DomainContract,
    DomainRuntime,
    DomainIR,
    VerbSpec,
)
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.compression.runtime import (
    ShannonEntropy,
    RunLengthCodec,
    HuffmanCodec,
    LZ77Codec,
    LZWCodec,
    ArithmeticCodec,
    compression_entropy,
    compression_rle_encode,
    compression_rle_decode,
    compression_huffman_encode,
    compression_huffman_decode,
    compression_lz77_encode,
    compression_lz77_decode,
    compression_lzw_encode,
    compression_lzw_decode,
    BWTCompressor,
    DeflateEngine,
    ByteAlignedSnappy,
    DeltaAndBitPackingEncoder,
    compression_bwt_compress,
    compression_bwt_decompress,
    compression_deflate,
    compression_inflate,
    compression_snappy_compress,
    compression_snappy_decompress,
    compression_delta_encode,
    compression_delta_decode,
)
from doomscript.domains.compression.parser import CompressionDomainParser
from doomscript.domains.compression.exporter import CompressionASTExporter


class CompressionRuntime(DomainRuntime):
    """Runtime coordinator for compression routines."""

    def execute_ir(self, ir: DomainIR, env: Dict[str, Any]) -> Any:
        return None


class CompressionDomain(DomainContract):
    """Domain contract for Compression & Information Theory."""

    name = "compression"
    aliases = ["compress", "huffman", "lzw", "codec"]
    description = "Lossless compression algorithms, RLE, Huffman prefix coding, LZ77, LZW, and Shannon entropy"
    parser = CompressionDomainParser()
    runtime = CompressionRuntime()
    exporter = CompressionASTExporter()
    capabilities = ["entropy", "huffman", "lzw", "lz77", "rle"]
    optional_dependencies = {}

    verbs = [
        VerbSpec(
            pattern="compress text {text:expr} with huffman into {target:ident}",
            description="Compresses text using canonical Huffman prefix coding",
        ),
        VerbSpec(
            pattern="decompress huffman {encoded:expr} into {target:ident}",
            description="Decompresses Huffman bitstream using codebook",
        ),
        VerbSpec(
            pattern="compress text {text:expr} with lzw into {target:ident}",
            description="Compresses text using LZW dictionary coding",
        ),
        VerbSpec(
            pattern="decompress lzw {codes:expr} into {target:ident}",
            description="Decompresses LZW token sequence",
        ),
        VerbSpec(
            pattern="calculate entropy of {text:expr} into {target:ident}",
            description="Calculates Shannon entropy in bits per symbol",
        ),
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        if self.parser.parse_inspect(line, 0) is not None or self.parser.parse_operation(line, 0) is not None:
            return True
        s = line.strip().lower()
        return (
            s.startswith("compress text ")
            or s.startswith("decompress huffman ")
            or s.startswith("decompress lzw ")
            or s.startswith("calculate entropy of ")
        )

    def can_handle_block(self, header: str) -> bool:
        return False


COMPRESSION_DOMAIN = CompressionDomain()
get_domain_registry().register(COMPRESSION_DOMAIN)

__all__ = [
    "CompressionDomain",
    "COMPRESSION_DOMAIN",
    "CompressionRuntime",
    "ShannonEntropy",
    "RunLengthCodec",
    "HuffmanCodec",
    "LZ77Codec",
    "LZWCodec",
    "ArithmeticCodec",
    "compression_entropy",
    "compression_rle_encode",
    "compression_rle_decode",
    "compression_huffman_encode",
    "compression_huffman_decode",
    "compression_lz77_encode",
    "compression_lz77_decode",
    "compression_lzw_encode",
    "compression_lzw_decode",
    "BWTCompressor",
    "DeflateEngine",
    "ByteAlignedSnappy",
    "DeltaAndBitPackingEncoder",
    "compression_bwt_compress",
    "compression_bwt_decompress",
    "compression_deflate",
    "compression_inflate",
    "compression_snappy_compress",
    "compression_snappy_decompress",
    "compression_delta_encode",
    "compression_delta_decode",
]
