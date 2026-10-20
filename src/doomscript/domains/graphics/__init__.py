"""Software Rasterization & Computer Graphics Domain Pack for DoomScript.

Enables native spoken-English framebuffers, 2D line/circle/rect rasterization,
and 3D Gouraud-shaded Z-buffered triangles via 'use graphics'.
"""

from typing import List, Optional, Dict, Any
from doomscript.domains.base import (
    DomainContract,
    DomainRuntime,
    DomainIR,
    VerbSpec,
)
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.graphics.runtime import (
    FrameBuffer,
    DepthBuffer,
    Rasterizer2D,
    Rasterizer3D,
    graphics_create_framebuffer,
    graphics_create_depthbuffer,
    graphics_draw_line,
    graphics_draw_circle,
    graphics_draw_rect,
    graphics_draw_triangle,
    BlinnPhongShader,
    BilinearTextureMapper,
    SuperSampledFrameBuffer,
    graphics_blinn_phong,
    graphics_sample_bilinear,
    graphics_supersampled_framebuffer,
    BresenhamWuAntiAliasedLine,
    PolygonScanlineActiveEdgeTableRasterizer,
    RayMarchingSignedDistanceFieldSDF,
    graphics_draw_wu_line,
    graphics_scanline_fill_polygon,
    graphics_ray_march_sdf,
)
from doomscript.domains.graphics.parser import GraphicsDomainParser
from doomscript.domains.graphics.exporter import GraphicsASTExporter


class GraphicsRuntime(DomainRuntime):
    """Runtime coordinator for software rendering routines."""

    def execute_ir(self, ir: DomainIR, env: Dict[str, Any]) -> Any:
        return None


class GraphicsDomain(DomainContract):
    """Domain contract for Software Rasterization & Computer Graphics."""

    name = "graphics"
    aliases = ["rendering", "framebuffer", "rasterizer", "draw"]
    description = "Pure Python software rendering, 2D/3D rasterization, framebuffers, and BMP/PPM export"
    parser = GraphicsDomainParser()
    runtime = GraphicsRuntime()
    exporter = GraphicsASTExporter()
    capabilities = ["framebuffer", "depthbuffer", "draw_line", "draw_circle", "draw_rect", "draw_triangle"]
    optional_dependencies = {}

    verbs = [
        VerbSpec(
            pattern="create framebuffer {w:expr} by {h:expr} into {target:ident}",
            description="Allocates 2D RGBA pixel buffer",
        ),
        VerbSpec(
            pattern="draw line on {fb:ident} from {x0:expr}, {y0:expr} to {x1:expr}, {y1:expr} with color {color:expr}",
            description="Draws 2D Bresenham line",
        ),
        VerbSpec(
            pattern="draw circle on {fb:ident} at {cx:expr}, {cy:expr} radius {r:expr} with color {color:expr}",
            description="Draws 2D midpoint circle",
        ),
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("create framebuffer ")
            or s.startswith("create canvas ")
            or s.startswith("draw line on ")
            or s.startswith("draw circle on ")
            or super().can_handle_line(line)
        )

    def can_handle_block(self, header: str) -> bool:
        return False


GRAPHICS_DOMAIN = GraphicsDomain()
get_domain_registry().register(GRAPHICS_DOMAIN)

__all__ = [
    "GraphicsDomain",
    "GRAPHICS_DOMAIN",
    "GraphicsRuntime",
    "FrameBuffer",
    "DepthBuffer",
    "Rasterizer2D",
    "Rasterizer3D",
    "graphics_create_framebuffer",
    "graphics_create_depthbuffer",
    "graphics_draw_line",
    "graphics_draw_circle",
    "graphics_draw_rect",
    "graphics_draw_triangle",
    "BlinnPhongShader",
    "BilinearTextureMapper",
    "SuperSampledFrameBuffer",
    "graphics_blinn_phong",
    "graphics_sample_bilinear",
    "graphics_supersampled_framebuffer",
    "BresenhamWuAntiAliasedLine",
    "PolygonScanlineActiveEdgeTableRasterizer",
    "RayMarchingSignedDistanceFieldSDF",
    "graphics_draw_wu_line",
    "graphics_scanline_fill_polygon",
    "graphics_ray_march_sdf",
]
