"""Shared visual identity: palette, fonts and drawing helpers.

Everything is drawn with Pygame primitives - no external art, no downloaded
fonts, nothing copyrighted.
"""

from __future__ import annotations

import math
from functools import lru_cache
from typing import Iterable, Sequence, Tuple

import pygame

Color = Tuple[int, int, int]

# ------------------------------------------------------------------ palette

BG = (7, 8, 20)
BG_DEEP = (3, 3, 10)
PANEL = (18, 20, 40)
GRID = (28, 32, 66)
TEXT = (232, 238, 255)
TEXT_DIM = (138, 148, 186)
CYAN = (0, 233, 255)
MAGENTA = (255, 45, 149)
LIME = (126, 255, 110)
AMBER = (255, 196, 62)
VIOLET = (170, 110, 255)
RED = (255, 74, 74)
WHITE = (255, 255, 255)

ACCENTS = (CYAN, MAGENTA, AMBER, LIME)

# -------------------------------------------------------------------- fonts

_FONT_CANDIDATES = ("consolas", "dejavusansmono", "couriernew", "monospace")


@lru_cache(maxsize=64)
def font(size: int, bold: bool = False) -> pygame.font.Font:
    """Monospace font at ``size``.  Falls back to Pygame's built-in font."""
    if not pygame.font.get_init():
        pygame.font.init()
    try:
        name = pygame.font.match_font(",".join(_FONT_CANDIDATES), bold=bold)
        if name:
            return pygame.font.Font(name, size)
    except Exception:
        pass
    return pygame.font.Font(None, int(size * 1.15))


def text_size(message: str, size: int, bold: bool = False) -> Tuple[int, int]:
    return font(size, bold).size(message)


def draw_text(
    surface: pygame.Surface,
    message: str,
    pos: Sequence[float],
    size: int = 24,
    color: Color = TEXT,
    align: str = "topleft",
    bold: bool = False,
    glow: float = 0.0,
    alpha: int = 255,
) -> pygame.Rect:
    """Draw text, optionally with a cheap glow (offset copies, no blur)."""
    face = font(size, bold)
    image = face.render(message, True, color)
    if alpha < 255:
        image = image.copy()
        image.set_alpha(alpha)
    rect = image.get_rect(**{align: (int(pos[0]), int(pos[1]))})
    if glow > 0.0:
        # Additive blits ignore the source alpha channel, and Pygame leaves the
        # text colour in fully-transparent pixels - so the halo has to be
        # flattened onto opaque black first, with the colour itself dimmed.
        # Intensity is quantised so the glow cache stays small under pulsing.
        pad = _glow_step(size) * 2
        surface.blit(_glow_text(message, size, bold, color,
                                round(min(1.0, glow) * (alpha / 255.0), 1)),
                     rect.move(-pad, -pad), special_flags=pygame.BLEND_ADD)
    surface.blit(image, rect)
    return rect


def _glow_step(size: int) -> int:
    """Halo offset in pixels for a given font size."""
    return max(1, int(size * 0.06))


@lru_cache(maxsize=256)
def _glow_text(message: str, size: int, bold: bool, color: Color, intensity: float) -> pygame.Surface:
    """Pre-flattened halo: four offset copies of the text on opaque black."""
    step = _glow_step(size)
    face = font(size, bold)
    dim = tuple(int(c * 0.22 * max(0.0, min(1.0, intensity))) for c in color)
    text = face.render(message, True, dim)
    halo = pygame.Surface((text.get_width() + step * 4, text.get_height() + step * 4))
    for dx, dy in ((0, step * 2), (step * 4, step * 2), (step * 2, 0), (step * 2, step * 4),
                   (step * 2, step * 2)):
        # Plain alpha blits here: BLEND_ADD would ignore the glyph mask and
        # smear the whole rectangle.
        halo.blit(text, (dx, dy))
    return halo


def draw_panel(
    surface: pygame.Surface,
    rect: pygame.Rect,
    color: Color = PANEL,
    border: Color | None = CYAN,
    alpha: int = 210,
    width: int = 2,
    radius: int = 12,
) -> None:
    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(panel, (*color, alpha), panel.get_rect(), border_radius=radius)
    surface.blit(panel, rect.topleft)
    if border:
        pygame.draw.rect(surface, border, rect, width=width, border_radius=radius)


def draw_bar(
    surface: pygame.Surface,
    rect: pygame.Rect,
    value: float,
    color: Color = CYAN,
    back: Color = (24, 26, 52),
    radius: int = 6,
    segments: int = 0,
) -> None:
    """Horizontal meter.  ``value`` is 0..1."""
    value = max(0.0, min(1.0, value))
    pygame.draw.rect(surface, back, rect, border_radius=radius)
    if value > 0.0:
        inner = pygame.Rect(rect.x, rect.y, max(2, int(rect.width * value)), rect.height)
        pygame.draw.rect(surface, color, inner, border_radius=radius)
    if segments > 1:
        for i in range(1, segments):
            x = rect.x + rect.width * i / segments
            pygame.draw.line(surface, BG, (x, rect.y), (x, rect.bottom), 1)
    pygame.draw.rect(surface, (*color, 255), rect, width=1, border_radius=radius)


def ascii_bar(value: float, width: int = 20) -> str:
    """``[========------------]`` style bar for the controller test screen."""
    value = max(0.0, min(1.0, value))
    filled = int(round(value * width))
    return "[" + "=" * filled + "-" * (width - filled) + "]"


def draw_glow_circle(surface: pygame.Surface, pos, radius: float, color: Color, layers: int = 3) -> None:
    """Additive halo around a solid dot.  Cheap: a few cached circle sprites."""
    sprite = _glow_circle_sprite(max(1, int(radius)), color, layers)
    offset = sprite.get_width() // 2
    surface.blit(sprite, (int(pos[0]) - offset, int(pos[1]) - offset), special_flags=pygame.BLEND_ADD)


@lru_cache(maxsize=256)
def _glow_circle_sprite(radius: int, color: Color, layers: int) -> pygame.Surface:
    # Built on opaque black because BLEND_ADD ignores per-pixel alpha.
    outer = int(radius * (1.0 + layers * 0.55)) + 2
    size = outer * 2
    sprite = pygame.Surface((size, size))
    centre = (outer, outer)
    for i in range(layers, 0, -1):
        shade = tuple(int(c * 0.16 / i) for c in color)
        pygame.draw.circle(sprite, shade, centre, int(radius * (1 + i * 0.55)))
    pygame.draw.circle(sprite, color, centre, radius)
    return sprite


def draw_glow_line(surface: pygame.Surface, start, end, color: Color, width: int = 2) -> None:
    pygame.draw.line(surface, tuple(c // 3 for c in color), start, end, width + 4)
    pygame.draw.line(surface, color, start, end, width)


def draw_scanlines(surface: pygame.Surface, alpha: int = 18, spacing: int = 3) -> None:
    overlay = _scanline_overlay(surface.get_size(), alpha, spacing)
    surface.blit(overlay, (0, 0))


@lru_cache(maxsize=8)
def _scanline_overlay(size: Tuple[int, int], alpha: int, spacing: int) -> pygame.Surface:
    overlay = pygame.Surface(size, pygame.SRCALPHA)
    for y in range(0, size[1], spacing):
        pygame.draw.line(overlay, (0, 0, 0, alpha), (0, y), (size[0], y))
    return overlay


def draw_vignette(surface: pygame.Surface, strength: int = 110) -> None:
    surface.blit(_vignette(surface.get_size(), strength), (0, 0))


@lru_cache(maxsize=8)
def _vignette(size: Tuple[int, int], strength: int) -> pygame.Surface:
    overlay = pygame.Surface(size, pygame.SRCALPHA)
    steps = 20
    width, height = size
    for i in range(steps):
        t = i / float(steps)
        alpha = int(strength * (1.0 - t) ** 2)
        band = int(min(width, height) * 0.06 * (1.0 - t) + 4)
        inset = int(min(width, height) * 0.35 * t)
        rect = pygame.Rect(inset, inset, width - inset * 2, height - inset * 2)
        if rect.width > band * 2 and rect.height > band * 2 and alpha > 0:
            pygame.draw.rect(overlay, (0, 0, 0, alpha // steps + 1), rect, width=band)
    return overlay


def draw_grid_background(surface: pygame.Surface, offset: float = 0.0, spacing: int = 64, color: Color = GRID) -> None:
    """Slowly scrolling neon grid used behind menus."""
    width, height = surface.get_size()
    surface.fill(BG)
    shift = offset % spacing
    for x in range(-spacing, width + spacing, spacing):
        pygame.draw.line(surface, color, (x + shift, 0), (x + shift, height), 1)
    for y in range(-spacing, height + spacing, spacing):
        pygame.draw.line(surface, color, (0, y + shift), (width, y + shift), 1)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def lerp_color(a: Color, b: Color, t: float) -> Color:
    t = max(0.0, min(1.0, t))
    return (int(lerp(a[0], b[0], t)), int(lerp(a[1], b[1], t)), int(lerp(a[2], b[2], t)))


def ease_out(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1.0 - (1.0 - t) ** 3


def pulse(time_s: float, speed: float = 3.0) -> float:
    """0..1 sine pulse, handy for blinking warnings."""
    return 0.5 + 0.5 * math.sin(time_s * speed)


def scale_value(surface_height: int, base: float) -> int:
    """Scale a design-space (720p) measurement to the live window."""
    return max(1, int(base * surface_height / 720.0))


def draw_control_hint(
    surface: pygame.Surface,
    rect: pygame.Rect,
    hints: Iterable[Tuple[str, str]],
    time_s: float = 0.0,
    accent: Color = CYAN,
) -> None:
    """Animated 'what do the knobs do' panel used by every game intro."""
    hints = list(hints)
    draw_panel(surface, rect, border=accent, alpha=190)
    row_h = rect.height / max(1, len(hints))
    for i, (label, action) in enumerate(hints):
        y = rect.y + row_h * (i + 0.5)
        wobble = math.sin(time_s * 2.4 + i * 0.8) * 4
        draw_text(surface, label, (rect.x + 22 + wobble, y), 22, accent, align="midleft", bold=True)
        draw_text(surface, action, (rect.right - 22, y), 22, TEXT, align="midright")
