"""Software Rasterization, 2D/3D Framebuffers & Computer Graphics Domain for DoomScript.

Provides a 100% pure Python software rendering pipeline:
- RGBA FrameBuffer with alpha blending and BMP/PPM export
- DepthBuffer (Z-buffer) for hidden surface removal
- Bresenham line algorithm (all 8 octants)
- Midpoint circle rasterizer (outline and filled)
- Sub-pixel accurate barycentric triangle rasterizer with Gouraud vertex color interpolation
Zero external dependencies.
"""

from __future__ import annotations

import math
import struct
from typing import Any, Dict, List, Optional, Tuple, Union


ColorRGB = Tuple[int, int, int]
ColorRGBA = Tuple[int, int, int, int]


class FrameBuffer:
    """2D pixel framebuffer supporting 32-bit RGBA color and alpha compositing."""

    def __init__(self, width: int, height: int, bg_color: ColorRGBA = (0, 0, 0, 255)):
        self.width = max(1, int(width))
        self.height = max(1, int(height))
        # Store as 1D list of (r, g, b, a) tuples
        self.pixels: List[ColorRGBA] = [bg_color] * (self.width * self.height)

    def clear(self, color: ColorRGBA = (0, 0, 0, 255)) -> None:
        """Clears all pixels in the framebuffer to color."""
        self.pixels = [color] * (self.width * self.height)

    def set_pixel(self, x: int, y: int, color: Union[ColorRGB, ColorRGBA]) -> None:
        """Sets pixel at (x, y) with alpha blending if color has alpha < 255."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return

        if len(color) == 3:
            r, g, b = color
            a = 255
        else:
            r, g, b, a = color

        idx = y * self.width + x

        if a == 255:
            self.pixels[idx] = (r, g, b, 255)
        elif a > 0:
            dst_r, dst_g, dst_b, dst_a = self.pixels[idx]
            alpha = a / 255.0
            inv_alpha = 1.0 - alpha
            out_r = int(r * alpha + dst_r * inv_alpha)
            out_g = int(g * alpha + dst_g * inv_alpha)
            out_b = int(b * alpha + dst_b * inv_alpha)
            self.pixels[idx] = (out_r, out_g, out_b, 255)

    def get_pixel(self, x: int, y: int) -> ColorRGBA:
        """Gets pixel at (x, y)."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return (0, 0, 0, 0)
        return self.pixels[y * self.width + x]

    def to_ppm(self) -> str:
        """Exports framebuffer to Netpbm P3 ASCII PPM format."""
        header = f"P3\n{self.width} {self.height}\n255\n"
        body = []
        for p in self.pixels:
            body.append(f"{p[0]} {p[1]} {p[2]}")
        return header + "\n".join(body) + "\n"

    def to_bmp(self) -> bytes:
        """Exports framebuffer to standard 24-bit Windows BMP image binary bytes."""
        row_bytes = self.width * 3
        padding = (4 - (row_bytes % 4)) % 4
        padded_row_size = row_bytes + padding
        image_data_size = padded_row_size * self.height
        file_size = 14 + 40 + image_data_size

        # BMP Header (14 bytes)
        # 'BM', FileSize (4B), Reserved (4B), Offset to Pixel Data (4B)
        bmp_header = struct.pack("<2sIHHI", b"BM", file_size, 0, 0, 54)

        # DIB Header (BITMAPINFOHEADER - 40 bytes)
        # HeaderSize(4B), W(4B), H(4B), Planes(2B), BPP(2B), Compression(4B), ImageSize(4B), Xppm(4B), Yppm(4B), ClrUsed(4B), ClrImp(4B)
        dib_header = struct.pack(
            "<IIIHHIIIIII",
            40,
            self.width,
            self.height,
            1,
            24,
            0,
            image_data_size,
            2835,  # 72 DPI
            2835,
            0,
            0,
        )

        # Pixel data (bottom-to-top, BGR order)
        pixel_bytes = bytearray()
        for y in range(self.height - 1, -1, -1):
            row = bytearray()
            for x in range(self.width):
                r, g, b, _ = self.pixels[y * self.width + x]
                row.append(b)
                row.append(g)
                row.append(r)
            row.extend(b"\x00" * padding)
            pixel_bytes.extend(row)

        return bmp_header + dib_header + bytes(pixel_bytes)


class DepthBuffer:
    """Z-buffer for hidden surface elimination."""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.buffer = [float("inf")] * (width * height)

    def clear(self) -> None:
        self.buffer = [float("inf")] * (self.width * self.height)

    def test_and_set(self, x: int, y: int, z: float) -> bool:
        """Returns True if fragment passes depth test and writes new z."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        idx = y * self.width + x
        if z < self.buffer[idx]:
            self.buffer[idx] = z
            return True
        return False


class Rasterizer2D:
    """2D Primitive Rasterization algorithms."""

    @staticmethod
    def draw_line(
        fb: FrameBuffer, x0: int, y0: int, x1: int, y1: int, color: Union[ColorRGB, ColorRGBA]
    ) -> None:
        """Bresenham's line algorithm supporting all 8 octants."""
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy

        while True:
            fb.set_pixel(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    @staticmethod
    def draw_circle(
        fb: FrameBuffer, cx: int, cy: int, radius: int, color: Union[ColorRGB, ColorRGBA], fill: bool = False
    ) -> None:
        """Midpoint circle algorithm."""
        cx, cy, r = int(cx), int(cy), int(radius)
        x = 0
        y = r
        d = 1 - r

        def plot_points(px: int, py: int):
            if fill:
                for line_x in range(cx - px, cx + px + 1):
                    fb.set_pixel(line_x, cy + py, color)
                    fb.set_pixel(line_x, cy - py, color)
                for line_x in range(cx - py, cx + py + 1):
                    fb.set_pixel(line_x, cy + px, color)
                    fb.set_pixel(line_x, cy - px, color)
            else:
                fb.set_pixel(cx + px, cy + py, color)
                fb.set_pixel(cx - px, cy + py, color)
                fb.set_pixel(cx + px, cy - py, color)
                fb.set_pixel(cx - px, cy - py, color)
                fb.set_pixel(cx + py, cy + px, color)
                fb.set_pixel(cx - py, cy + px, color)
                fb.set_pixel(cx + py, cy - px, color)
                fb.set_pixel(cx - py, cy - px, color)

        plot_points(x, y)
        while x < y:
            x += 1
            if d < 0:
                d += 2 * x + 1
            else:
                y -= 1
                d += 2 * (x - y) + 1
            plot_points(x, y)

    @staticmethod
    def draw_rect(
        fb: FrameBuffer, x: int, y: int, w: int, h: int, color: Union[ColorRGB, ColorRGBA], fill: bool = False
    ) -> None:
        """Draws axis-aligned rectangle."""
        x, y, w, h = int(x), int(y), int(w), int(h)
        if fill:
            for cur_y in range(y, y + h):
                for cur_x in range(x, x + w):
                    fb.set_pixel(cur_x, cur_y, color)
        else:
            Rasterizer2D.draw_line(fb, x, y, x + w - 1, y, color)
            Rasterizer2D.draw_line(fb, x + w - 1, y, x + w - 1, y + h - 1, color)
            Rasterizer2D.draw_line(fb, x + w - 1, y + h - 1, x, y + h - 1, color)
            Rasterizer2D.draw_line(fb, x, y + h - 1, x, y, color)


class Rasterizer3D:
    """3D Triangle Rasterization with Z-Buffering and Barycentric Gouraud Shading."""

    @staticmethod
    def draw_triangle(
        fb: FrameBuffer,
        zb: DepthBuffer,
        v0: Tuple[float, float, float],
        v1: Tuple[float, float, float],
        v2: Tuple[float, float, float],
        c0: ColorRGB,
        c1: ColorRGB,
        c2: ColorRGB,
    ) -> None:
        """Rasterizes a 3D triangle using barycentric coordinates, interpolating depth and vertex colors."""
        x0, y0, z0 = v0
        x1, y1, z1 = v1
        x2, y2, z2 = v2

        # Bounding box
        min_x = max(0, int(math.floor(min(x0, x1, x2))))
        max_x = min(fb.width - 1, int(math.ceil(max(x0, x1, x2))))
        min_y = max(0, int(math.floor(min(y0, y1, y2))))
        max_y = min(fb.height - 1, int(math.ceil(max(y0, y1, y2))))

        denom = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(denom) < 1e-9:
            # Degenerate triangle
            return

        inv_denom = 1.0 / denom

        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                px = x + 0.5
                py = y + 0.5

                # Barycentric weights
                w0 = ((y1 - y2) * (px - x2) + (x2 - x1) * (py - y2)) * inv_denom
                w1 = ((y2 - y0) * (px - x2) + (x0 - x2) * (py - y2)) * inv_denom
                w2 = 1.0 - w0 - w1

                # Point inside triangle test
                if w0 >= 0 and w1 >= 0 and w2 >= 0:
                    # Interpolate depth
                    z = w0 * z0 + w1 * z1 + w2 * z2
                    if zb.test_and_set(x, y, z):
                        # Interpolate Gouraud vertex colors
                        r = int(min(255, max(0, w0 * c0[0] + w1 * c1[0] + w2 * c2[0])))
                        g = int(min(255, max(0, w0 * c0[1] + w1 * c1[1] + w2 * c2[1])))
                        b = int(min(255, max(0, w0 * c0[2] + w1 * c1[2] + w2 * c2[2])))
                        fb.set_pixel(x, y, (r, g, b, 255))


# --- High-Level Public Functions ---

def graphics_create_framebuffer(width: int, height: int, bg_color: ColorRGBA = (0, 0, 0, 255)) -> FrameBuffer:
    """Creates a new FrameBuffer."""
    return FrameBuffer(width, height, bg_color)


def graphics_create_depthbuffer(width: int, height: int) -> DepthBuffer:
    """Creates a new DepthBuffer (Z-buffer)."""
    return DepthBuffer(width, height)


def graphics_draw_line(
    fb: FrameBuffer, x0: int, y0: int, x1: int, y1: int, color: Union[ColorRGB, ColorRGBA]
) -> None:
    """Draws a 2D line using Bresenham's algorithm."""
    Rasterizer2D.draw_line(fb, x0, y0, x1, y1, color)


def graphics_draw_circle(
    fb: FrameBuffer, cx: int, cy: int, radius: int, color: Union[ColorRGB, ColorRGBA], fill: bool = False
) -> None:
    """Draws a 2D circle using the midpoint algorithm."""
    Rasterizer2D.draw_circle(fb, cx, cy, radius, color, fill)


def graphics_draw_rect(
    fb: FrameBuffer, x: int, y: int, w: int, h: int, color: Union[ColorRGB, ColorRGBA], fill: bool = False
) -> None:
    """Draws a 2D rectangle."""
    Rasterizer2D.draw_rect(fb, x, y, w, h, color, fill)


def graphics_draw_triangle(
    fb: FrameBuffer,
    zb: DepthBuffer,
    v0: Tuple[float, float, float],
    v1: Tuple[float, float, float],
    v2: Tuple[float, float, float],
    c0: ColorRGB,
    c1: ColorRGB,
    c2: ColorRGB,
) -> None:
    """Draws a 3D triangle with Z-buffer and Gouraud color shading."""
    Rasterizer3D.draw_triangle(fb, zb, v0, v1, v2, c0, c1, c2)


class BlinnPhongShader:
    """Blinn-Phong lighting calculation for 3D fragments."""

    def __init__(
        self,
        ambient_light: Tuple[float, float, float] = (0.2, 0.2, 0.2),
        light_color: Tuple[float, float, float] = (1.0, 1.0, 1.0),
        light_pos: Tuple[float, float, float] = (5.0, 10.0, -5.0),
        camera_pos: Tuple[float, float, float] = (0.0, 0.0, -5.0),
    ):
        self.ambient_light = ambient_light
        self.light_color = light_color
        self.light_pos = light_pos
        self.camera_pos = camera_pos

    def shade_fragment(
        self,
        frag_pos: Tuple[float, float, float],
        frag_normal: Tuple[float, float, float],
        diffuse_color: Tuple[float, float, float],
        specular_color: Tuple[float, float, float] = (1.0, 1.0, 1.0),
        shininess: float = 32.0,
        ka: float = 1.0,
        kd: float = 0.8,
        ks: float = 0.5,
    ) -> Tuple[int, int, int]:
        """Calculates shaded RGB color in range [0, 255]."""
        # Vectors: N, L, V, H
        def norm(v: Tuple[float, float, float]) -> Tuple[float, float, float]:
            l = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2) or 1.0
            return (v[0] / l, v[1] / l, v[2] / l)

        def dot(v1: Tuple[float, float, float], v2: Tuple[float, float, float]) -> float:
            return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]

        N = norm(frag_normal)
        L = norm((self.light_pos[0] - frag_pos[0], self.light_pos[1] - frag_pos[1], self.light_pos[2] - frag_pos[2]))
        V = norm((self.camera_pos[0] - frag_pos[0], self.camera_pos[1] - frag_pos[1], self.camera_pos[2] - frag_pos[2]))
        H = norm((L[0] + V[0], L[1] + V[1], L[2] + V[2]))

        # Ambient
        I_amb = [ka * self.ambient_light[i] * diffuse_color[i] for i in range(3)]

        # Diffuse Lambertian
        n_dot_l = max(0.0, dot(N, L))
        I_diff = [kd * n_dot_l * self.light_color[i] * diffuse_color[i] for i in range(3)]

        # Specular Blinn-Phong
        n_dot_h = max(0.0, dot(N, H))
        spec_factor = (n_dot_h ** shininess) if n_dot_l > 0 else 0.0
        I_spec = [ks * spec_factor * self.light_color[i] * specular_color[i] for i in range(3)]

        total_r = min(255, max(0, int((I_amb[0] + I_diff[0] + I_spec[0]) * 255)))
        total_g = min(255, max(0, int((I_amb[1] + I_diff[1] + I_spec[1]) * 255)))
        total_b = min(255, max(0, int((I_amb[2] + I_diff[2] + I_spec[2]) * 255)))

        return (total_r, total_g, total_b)


class BilinearTextureMapper:
    """Texture buffer supporting bilinear 4-tap UV filtering."""

    def __init__(self, width: int, height: int, pixels: Optional[List[Tuple[int, int, int]]] = None):
        self.width = width
        self.height = height
        self.pixels = list(pixels or [(255, 255, 255)] * (width * height))

    def sample(self, u: float, v: float) -> Tuple[int, int, int]:
        """Samples texture with bilinear interpolation for coordinates u, v in [0, 1]."""
        u_clamped = max(0.0, min(1.0, float(u)))
        v_clamped = max(0.0, min(1.0, float(v)))

        gx = u_clamped * (self.width - 1)
        gy = v_clamped * (self.height - 1)

        x0 = int(math.floor(gx))
        x1 = min(self.width - 1, x0 + 1)
        y0 = int(math.floor(gy))
        y1 = min(self.height - 1, y0 + 1)

        s = gx - x0
        t = gy - y0

        c00 = self.pixels[y0 * self.width + x0]
        c10 = self.pixels[y0 * self.width + x1]
        c01 = self.pixels[y1 * self.width + x0]
        c11 = self.pixels[y1 * self.width + x1]

        r = int(round((1 - s) * (1 - t) * c00[0] + s * (1 - t) * c10[0] + (1 - s) * t * c01[0] + s * t * c11[0]))
        g = int(round((1 - s) * (1 - t) * c00[1] + s * (1 - t) * c10[1] + (1 - s) * t * c01[1] + s * t * c11[1]))
        b = int(round((1 - s) * (1 - t) * c00[2] + s * (1 - t) * c10[2] + (1 - s) * t * c01[2] + s * t * c11[2]))

        return (min(255, max(0, r)), min(255, max(0, g)), min(255, max(0, b)))


class SuperSampledFrameBuffer:
    """Supersampling Anti-Aliasing (SSAA) framebuffer with 2x2 or 4x4 sub-pixel downsampler."""

    def __init__(self, target_width: int, target_height: int, scale: int = 2):
        self.target_width = target_width
        self.target_height = target_height
        self.scale = max(2, int(scale))
        self.render_width = target_width * self.scale
        self.render_height = target_height * self.scale
        self.fb = FrameBuffer(self.render_width, self.render_height)

    def set_subpixel(self, x: int, y: int, color: Tuple[int, int, int]) -> None:
        self.fb.set_pixel(x, y, color)

    def downsample(self) -> FrameBuffer:
        """Averages subpixels down to target dimensions."""
        output_fb = FrameBuffer(self.target_width, self.target_height)
        s2 = self.scale * self.scale

        for ty in range(self.target_height):
            for tx in range(self.target_width):
                total_r = 0
                total_g = 0
                total_b = 0
                total_a = 0

                for sy in range(self.scale):
                    for sx in range(self.scale):
                        rx = tx * self.scale + sx
                        ry = ty * self.scale + sy
                        pixel = self.fb.get_pixel(rx, ry)
                        total_r += pixel[0]
                        total_g += pixel[1]
                        total_b += pixel[2]
                        total_a += pixel[3]

                avg_pixel = (
                    int(total_r / s2),
                    int(total_g / s2),
                    int(total_b / s2),
                    int(total_a / s2),
                )
                output_fb.set_pixel(tx, ty, avg_pixel)

        return output_fb


def graphics_blinn_phong(
    frag_pos: Tuple[float, float, float],
    frag_normal: Tuple[float, float, float],
    diffuse_color: Tuple[float, float, float],
) -> Tuple[int, int, int]:
    """Calculates Blinn-Phong shading on a 3D surface fragment."""
    shader = BlinnPhongShader()
    return shader.shade_fragment(frag_pos, frag_normal, diffuse_color)


def graphics_sample_bilinear(tex: BilinearTextureMapper, u: float, v: float) -> Tuple[int, int, int]:
    """Samples texture using 4-tap bilinear interpolation."""
    return tex.sample(u, v)


def graphics_supersampled_framebuffer(width: int, height: int, scale: int = 2) -> SuperSampledFrameBuffer:
    """Creates a high-resolution SSAA FrameBuffer."""
    return SuperSampledFrameBuffer(width, height, scale)

