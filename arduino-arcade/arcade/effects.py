"""Juice: particles, screen shake, floating text, starfields.

All systems are bounded - particle lists are capped so a long session can
never turn into a slideshow or leak memory.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import List, Tuple

import pygame

from . import ui

MAX_PARTICLES = 420


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float
    color: Tuple[int, int, int]
    size: float
    gravity: float = 0.0
    drag: float = 0.0
    kind: str = "dot"


class ParticleSystem:
    def __init__(self, max_particles: int = MAX_PARTICLES):
        self.particles: List[Particle] = []
        self.max_particles = max_particles

    def __len__(self) -> int:
        return len(self.particles)

    def clear(self) -> None:
        self.particles.clear()

    def add(self, particle: Particle) -> None:
        if len(self.particles) >= self.max_particles:
            # Drop the oldest rather than refusing new ones: the newest
            # effects are the ones the player is actually looking at.
            del self.particles[0]
        self.particles.append(particle)

    def burst(
        self,
        pos,
        count: int = 14,
        color=ui.CYAN,
        speed: float = 220.0,
        life: float = 0.55,
        spread: float = math.tau,
        direction: float = 0.0,
        size: float = 3.0,
        gravity: float = 0.0,
        drag: float = 1.6,
        kind: str = "dot",
    ) -> None:
        for _ in range(count):
            angle = direction + random.uniform(-spread / 2, spread / 2)
            velocity = speed * random.uniform(0.35, 1.0)
            self.add(
                Particle(
                    pos[0], pos[1],
                    math.cos(angle) * velocity, math.sin(angle) * velocity,
                    life * random.uniform(0.6, 1.25), life,
                    color, size * random.uniform(0.6, 1.5),
                    gravity, drag, kind,
                )
            )

    def trail(self, pos, color=ui.CYAN, count: int = 2, spread: float = 40.0, life: float = 0.3, size: float = 2.5) -> None:
        for _ in range(count):
            self.add(
                Particle(
                    pos[0] + random.uniform(-3, 3), pos[1] + random.uniform(-3, 3),
                    random.uniform(-spread, spread), random.uniform(-spread, spread),
                    life * random.uniform(0.5, 1.0), life, color, size, 0.0, 2.0,
                )
            )

    def update(self, dt: float) -> None:
        alive = []
        for p in self.particles:
            p.life -= dt
            if p.life <= 0:
                continue
            p.vy += p.gravity * dt
            if p.drag:
                damp = max(0.0, 1.0 - p.drag * dt)
                p.vx *= damp
                p.vy *= damp
            p.x += p.vx * dt
            p.y += p.vy * dt
            alive.append(p)
        self.particles = alive

    def draw(self, surface: pygame.Surface, offset=(0, 0)) -> None:
        for p in self.particles:
            t = max(0.0, min(1.0, p.life / max(p.max_life, 1e-4)))
            x, y = int(p.x + offset[0]), int(p.y + offset[1])
            color = tuple(int(c * t) for c in p.color)
            if p.kind == "spark":
                pygame.draw.line(
                    surface, color, (x, y),
                    (int(x - p.vx * 0.02), int(y - p.vy * 0.02)),
                    max(1, int(p.size * 0.6)),
                )
            elif p.kind == "square":
                size = max(1, int(p.size * t * 2))
                pygame.draw.rect(surface, color, (x, y, size, size))
            else:
                radius = max(1, int(p.size * t))
                pygame.draw.circle(surface, color, (x, y), radius)


class ScreenShake:
    """Decaying random offset.  Use sparingly - big hits only."""

    def __init__(self):
        self.amount = 0.0
        self.offset = (0.0, 0.0)

    def add(self, amount: float, cap: float = 26.0) -> None:
        self.amount = min(cap, self.amount + amount)

    def update(self, dt: float) -> None:
        self.amount = max(0.0, self.amount - self.amount * 6.0 * dt - 6.0 * dt)
        if self.amount > 0.05:
            self.offset = (
                random.uniform(-self.amount, self.amount),
                random.uniform(-self.amount, self.amount),
            )
        else:
            self.offset = (0.0, 0.0)

    def reset(self) -> None:
        self.amount = 0.0
        self.offset = (0.0, 0.0)


@dataclass
class FloatingText:
    text: str
    x: float
    y: float
    color: Tuple[int, int, int]
    life: float = 1.0
    max_life: float = 1.0
    size: int = 26
    vy: float = -46.0


class FloatingTextSystem:
    def __init__(self, limit: int = 40):
        self.items: List[FloatingText] = []
        self.limit = limit

    def add(self, text: str, pos, color=ui.AMBER, size: int = 26, life: float = 1.0) -> None:
        if len(self.items) >= self.limit:
            del self.items[0]
        self.items.append(FloatingText(text, pos[0], pos[1], color, life, life, size))

    def clear(self) -> None:
        self.items.clear()

    def update(self, dt: float) -> None:
        for item in self.items:
            item.life -= dt
            item.y += item.vy * dt
        self.items = [i for i in self.items if i.life > 0]

    def draw(self, surface: pygame.Surface, offset=(0, 0)) -> None:
        for item in self.items:
            t = max(0.0, min(1.0, item.life / max(item.max_life, 1e-4)))
            scale = 1.0 + (1.0 - t) * 0.25
            ui.draw_text(
                surface, item.text,
                (item.x + offset[0], item.y + offset[1]),
                int(item.size * scale), item.color,
                align="center", bold=True, alpha=int(255 * t), glow=t,
            )


class Starfield:
    """Parallax star layers, used behind menus and Orbital Defender."""

    def __init__(self, size, count: int = 90, speed: float = 26.0):
        self.size = size
        self.speed = speed
        self.stars = [
            [random.uniform(0, size[0]), random.uniform(0, size[1]), random.uniform(0.35, 1.0)]
            for _ in range(count)
        ]

    def resize(self, size) -> None:
        old = self.size
        self.size = size
        for star in self.stars:
            star[0] = star[0] / max(1, old[0]) * size[0]
            star[1] = star[1] / max(1, old[1]) * size[1]

    def update(self, dt: float, drift: float = 1.0) -> None:
        for star in self.stars:
            star[1] += self.speed * star[2] * drift * dt
            if star[1] > self.size[1]:
                star[1] = -2
                star[0] = random.uniform(0, self.size[0])

    def draw(self, surface: pygame.Surface) -> None:
        for x, y, depth in self.stars:
            shade = int(70 + 165 * depth)
            pygame.draw.circle(surface, (shade, shade, min(255, shade + 30)), (int(x), int(y)), 1 if depth < 0.7 else 2)


def flash_surface(size, color, alpha: int) -> pygame.Surface:
    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.fill((*color, max(0, min(255, alpha))))
    return surface


@dataclass
class Transition:
    """Simple wipe used between scenes."""

    duration: float = 0.35
    elapsed: float = field(default=0.0)
    closing: bool = True

    @property
    def done(self) -> bool:
        return self.elapsed >= self.duration

    @property
    def progress(self) -> float:
        return max(0.0, min(1.0, self.elapsed / max(self.duration, 1e-4)))

    def update(self, dt: float) -> None:
        self.elapsed += dt

    def draw(self, surface: pygame.Surface) -> None:
        t = ui.ease_out(self.progress)
        cover = t if self.closing else 1.0 - t
        if cover <= 0.001:
            return
        width, height = surface.get_size()
        band = int(height * 0.5 * cover)
        overlay = pygame.Surface((width, band), pygame.SRCALPHA)
        overlay.fill((*ui.BG_DEEP, 255))
        surface.blit(overlay, (0, 0))
        surface.blit(overlay, (0, height - band))
        pygame.draw.line(surface, ui.CYAN, (0, band), (width, band), 2)
        pygame.draw.line(surface, ui.MAGENTA, (0, height - band), (width, height - band), 2)
