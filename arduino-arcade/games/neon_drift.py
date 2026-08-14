"""NEON DRIFT - endless pseudo-3D neon highway racer.

POT 1 steers, POT 2 is the throttle, B1 boosts, B2 drifts/brakes,
B3 uses a stored power-up, B4 is the emergency recentre.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

import pygame

from arcade import ui
from arcade.game import BaseGame, approach, clamp

HORIZON_RATIO = 0.42
ROW_STEP = 5            # pixels between road strips
DRAW_DISTANCE = 92.0    # world units visible ahead (matches the row table)
ROAD_HALF_WIDTH = 1.0   # lateral units from centre to edge
ROAD_SCREEN_FRAC = 0.42  # road half-width at the bottom, as a fraction of the window
CURVE_STRENGTH = 0.30    # how hard the road bends away from the camera

MAX_SPEED = 340.0       # world units / second at full throttle
BOOST_SPEED = 520.0
MIN_SPEED = 70.0
MAX_DAMAGE = 3

POWERUPS = ("SHIELD", "NITRO", "GHOST")


@dataclass
class RoadObject:
    z: float
    x: float           # lateral position, -1..1 across the road
    kind: str          # "traffic" | "hazard" | "pickup"
    color: Tuple[int, int, int]
    speed: float = 0.0
    width: float = 0.34
    passed: bool = False
    near_missed: bool = False
    alive: bool = True
    powerup: str = ""


class NeonDrift(BaseGame):
    game_id = "neon_drift"
    title = "NEON DRIFT"
    subtitle = "ENDLESS NEON HIGHWAY"
    accent = ui.MAGENTA
    control_hints = (
        ("POT 1", "STEER LEFT / RIGHT"),
        ("POT 2", "THROTTLE"),
        ("BUTTON 1", "BOOST"),
        ("BUTTON 2", "DRIFT / BRAKE"),
        ("BUTTON 3", "USE POWER-UP"),
        ("BUTTON 4", "EMERGENCY RECENTRE"),
    )

    def __init__(self, app):
        super().__init__(app)
        self.reset_game()

    # ------------------------------------------------------------- state

    def reset_game(self) -> None:
        self.score = 0.0
        self.distance = 0.0
        self.speed = MIN_SPEED
        self.player_x = 0.0
        self.player_vx = 0.0
        self.steer_target = 0.0
        self.boost_meter = 1.0
        self.boosting = False
        self.drifting = False
        self.damage = 0
        self.combo = 1.0
        self.best_combo = 1.0
        self.combo_timer = 0.0
        self.invulnerable = 0.0
        self.ghost_timer = 0.0
        self.nitro_timer = 0.0
        self.powerup: Optional[str] = None
        self.objects: List[RoadObject] = []
        self.spawn_timer = 1.2
        self.difficulty = 0.0
        self.curve_seed = random.uniform(0, 1000)
        self.road_rows: List[Tuple[int, float, float, float]] = []
        self.hit_flash = 0.0
        self.speed_lines: List[List[float]] = []

    # -------------------------------------------------------------- road

    def curve_at(self, z: float) -> float:
        """Smooth endless curvature in the range roughly -1.6..1.6."""
        s = self.curve_seed
        return (
            1.05 * math.sin((z + s) * 0.0021)
            + 0.65 * math.sin((z + s) * 0.00072 + 1.7)
            + 0.35 * math.sin((z + s) * 0.0045 + 0.4)
        )

    def _build_rows(self, surface: pygame.Surface) -> None:
        """Project the road once per frame; everything else reuses the table."""
        width, height = surface.get_size()
        horizon = int(height * HORIZON_RATIO)
        rows = []
        camera_curve = self.curve_at(self.distance)
        for y in range(height, horizon, -ROW_STEP):
            # depth: 1 at the bottom of the screen, approaching 0 at the horizon.
            depth = (y - horizon) / float(height - horizon)
            # Flat-road perspective: screen width tapers linearly with depth,
            # and world distance is its reciprocal.
            d = 1.0 / max(0.004, depth) - 1.0
            if d > DRAW_DISTANCE:
                break
            z = self.distance + d
            half_w = width * ROAD_SCREEN_FRAC * depth
            bend = (self.curve_at(z) - camera_curve) * width * CURVE_STRENGTH * (1.0 - depth)
            centre = width * 0.5 + bend - self.player_x * half_w
            rows.append((y, centre, half_w, d))
        self.road_rows = rows

    def _row_for_distance(self, d: float):
        """Interpolate the projected road table at world distance ``d``."""
        rows = self.road_rows
        if not rows or d < 0:
            return None
        previous = rows[0]
        for row in rows:
            if row[3] >= d:
                span = row[3] - previous[3]
                t = 0.0 if span <= 1e-5 else (d - previous[3]) / span
                return (
                    previous[0] + (row[0] - previous[0]) * t,
                    previous[1] + (row[1] - previous[1]) * t,
                    previous[2] + (row[2] - previous[2]) * t,
                )
            previous = row
        return None

    # ---------------------------------------------------------- gameplay

    def _spawn(self) -> None:
        self.difficulty = min(1.0, self.distance / 26000.0)
        roll = random.random()
        z = self.distance + DRAW_DISTANCE * random.uniform(0.92, 1.0)
        lane = random.choice((-0.66, -0.33, 0.0, 0.33, 0.66))
        if roll < 0.16 - 0.05 * self.difficulty:
            self.objects.append(RoadObject(z, lane, "pickup", ui.LIME, width=0.2,
                                           powerup=random.choice(POWERUPS)))
        elif roll < 0.42:
            self.objects.append(RoadObject(z, lane, "hazard", ui.AMBER, width=0.24))
        else:
            self.objects.append(RoadObject(z, lane, "traffic", random.choice((ui.CYAN, ui.VIOLET, ui.MAGENTA)),
                                           speed=random.uniform(60.0, 150.0)))
        self.spawn_timer = random.uniform(0.35, 0.95) * (1.0 - 0.45 * self.difficulty)

    def update_play(self, dt: float, controller) -> None:
        width, height = self.size
        self.hit_flash = max(0.0, self.hit_flash - dt * 3.0)
        self.invulnerable = max(0.0, self.invulnerable - dt)
        self.ghost_timer = max(0.0, self.ghost_timer - dt)
        self.nitro_timer = max(0.0, self.nitro_timer - dt)

        # --- steering: pot 1 maps directly to a target lane position ------
        self.steer_target = (controller.pot1 - 0.5) * 2.0 * 1.15
        self.drifting = controller.button2
        grip = 7.5 if not self.drifting else 3.4
        self.player_vx = approach(self.player_vx, (self.steer_target - self.player_x) * grip, 12.0, dt)

        # Centrifugal push from the curve scales with speed - the road fights back.
        curve = self.curve_at(self.distance)
        self.player_vx -= curve * (self.speed / MAX_SPEED) * 0.85 * dt * 5.0
        self.player_x += self.player_vx * dt
        self.player_x = clamp(self.player_x, -1.45, 1.45)

        # --- throttle / boost --------------------------------------------
        throttle = controller.pot2
        target = MIN_SPEED + (MAX_SPEED - MIN_SPEED) * throttle
        self.boosting = controller.button1 and self.boost_meter > 0.0
        if self.boosting:
            target = BOOST_SPEED
            self.boost_meter = max(0.0, self.boost_meter - dt * 0.42)
            self.particles.trail(
                (width * 0.5 + self.player_x * width * 0.2, height * 0.86),
                ui.AMBER, count=2, spread=90, life=0.35, size=4,
            )
        else:
            self.boost_meter = min(1.0, self.boost_meter + dt * 0.14)
        if self.nitro_timer > 0.0:
            target = max(target, BOOST_SPEED * 0.95)
        if self.drifting:
            target *= 0.55
        self.speed = approach(self.speed, target, 2.6 if target > self.speed else 4.0, dt)
        self.distance += self.speed * dt

        # --- scoring ------------------------------------------------------
        if self.combo_timer > 0.0:
            self.combo_timer -= dt
            if self.combo_timer <= 0.0:
                self.combo = 1.0
        self.score += self.speed * dt * 0.35 * self.combo

        # --- traffic ------------------------------------------------------
        self.spawn_timer -= dt
        if self.spawn_timer <= 0.0:
            self._spawn()
        self._update_objects(dt)

        # --- power-up use --------------------------------------------------
        if controller.button_pressed(3) and self.powerup:
            self._use_powerup()
        if controller.button_pressed(4):
            self._emergency_recentre()

        # --- off-road penalty ---------------------------------------------
        if abs(self.player_x) > ROAD_HALF_WIDTH + 0.05:
            self.speed = max(MIN_SPEED * 0.7, self.speed - 140.0 * dt)
            self.shake.add(2.2)
            if random.random() < 0.4:
                self.particles.burst((width * 0.5 + self.player_x * 60, height * 0.9), 3,
                                     ui.AMBER, speed=180, life=0.35, size=2.5)

        self._update_speed_lines(dt)

    def _update_objects(self, dt: float) -> None:
        remaining = []
        for obj in self.objects:
            obj.z += obj.speed * dt
            d = obj.z - self.distance
            if d < -18.0 or not obj.alive:
                continue
            if 0.0 <= d <= 2.6 and not obj.passed:
                obj.passed = True
                gap = abs(obj.x - self.player_x)
                hit_gap = obj.width + 0.16
                if gap < hit_gap and obj.kind != "pickup":
                    self._crash(obj)
                elif obj.kind == "pickup" and gap < hit_gap + 0.1:
                    self._collect(obj)
                    continue
                elif gap < hit_gap + 0.3:
                    self._near_miss(obj)
            remaining.append(obj)
        self.objects = remaining

    def _crash(self, obj: RoadObject) -> None:
        if self.invulnerable > 0.0 or self.ghost_timer > 0.0:
            return
        width, height = self.size
        self.app.audio.play("collision")
        self.shake.add(18.0)
        self.hit_flash = 1.0
        self.speed *= 0.42
        self.combo = 1.0
        self.combo_timer = 0.0
        self.invulnerable = 1.4
        self.damage += 1
        obj.alive = False
        self.particles.burst((width * 0.5, height * 0.82), 34, ui.RED, speed=380, life=0.7,
                             size=4, gravity=260, kind="spark")
        self.floaters.add("CRASH!", (width * 0.5, height * 0.6), ui.RED, 40, 1.1)
        if self.damage >= MAX_DAMAGE:
            self.game_over("WRECKED")

    def _near_miss(self, obj: RoadObject) -> None:
        if obj.near_missed:
            return
        obj.near_missed = True
        width, height = self.size
        self.combo = min(8.0, self.combo + 0.5)
        self.best_combo = max(self.best_combo, self.combo)
        self.combo_timer = 3.0
        gain = int(120 * self.combo)
        self.score += gain
        self.boost_meter = min(1.0, self.boost_meter + 0.08)
        self.app.audio.play("combo", 0.6)
        self.floaters.add(f"NEAR MISS x{self.combo:.1f}  +{gain}",
                          (width * 0.5, height * 0.55), ui.CYAN, 28, 0.9)
        self.particles.burst((width * 0.5 + obj.x * 140, height * 0.7), 8, ui.CYAN, speed=200, life=0.4)

    def _collect(self, obj: RoadObject) -> None:
        obj.alive = False
        self.powerup = obj.powerup
        self.app.audio.play("powerup")
        width, height = self.size
        self.floaters.add(f"{obj.powerup} READY  [B3]", (width * 0.5, height * 0.5), ui.LIME, 30, 1.2)
        self.particles.burst((width * 0.5, height * 0.75), 18, ui.LIME, speed=260, life=0.6)

    def _use_powerup(self) -> None:
        width, height = self.size
        name, self.powerup = self.powerup, None
        self.app.audio.play("boost")
        if name == "SHIELD":
            self.invulnerable = 6.0
        elif name == "NITRO":
            self.nitro_timer = 4.0
            self.boost_meter = 1.0
        else:  # GHOST
            self.ghost_timer = 5.0
        self.floaters.add(f"{name}!", (width * 0.5, height * 0.45), ui.AMBER, 40, 1.0)
        self.particles.burst((width * 0.5, height * 0.85), 26, ui.AMBER, speed=320, life=0.7)

    def _emergency_recentre(self) -> None:
        width, height = self.size
        self.player_x = approach(self.player_x, 0.0, 1.0, 1.0)
        self.player_vx = 0.0
        self.speed *= 0.75
        self.combo = 1.0
        self.invulnerable = max(self.invulnerable, 0.9)
        self.app.audio.play("shield")
        self.floaters.add("RECENTRE", (width * 0.5, height * 0.66), ui.VIOLET, 26, 0.7)

    def _update_speed_lines(self, dt: float) -> None:
        width, height = self.size
        intensity = self.speed / BOOST_SPEED
        if random.random() < intensity * 0.9:
            side = random.choice((-1, 1))
            self.speed_lines.append([
                width * 0.5 + side * random.uniform(width * 0.12, width * 0.55),
                random.uniform(height * HORIZON_RATIO, height),
                random.uniform(0.25, 0.5),
            ])
        for line in self.speed_lines:
            line[2] -= dt
        if len(self.speed_lines) > 90:
            del self.speed_lines[: len(self.speed_lines) - 90]
        self.speed_lines = [line for line in self.speed_lines if line[2] > 0]

    # ------------------------------------------------------------- render

    def draw_background(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        horizon = int(height * HORIZON_RATIO)
        surface.fill(ui.BG_DEEP)
        # Sky gradient in a handful of bands (cheap, no per-pixel work).
        for i in range(12):
            t = i / 12.0
            color = ui.lerp_color((10, 4, 30), (58, 10, 74), t)
            pygame.draw.rect(surface, color, (0, int(horizon * t), width, int(horizon / 12) + 2))
        # Distant sun + skyline.
        sun_y = horizon - int(height * 0.1)
        ui.draw_glow_circle(surface, (width // 2, sun_y), height * 0.09, (255, 90, 160), layers=3)
        offset = int(self.distance * 0.35) % 200
        for i in range(-1, width // 90 + 2):
            x = i * 90 - offset % 90
            h = 20 + (i * 37 + int(self.curve_seed)) % 70
            pygame.draw.rect(surface, (24, 12, 48), (x, horizon - h, 54, h))
            pygame.draw.rect(surface, (70, 30, 110), (x, horizon - h, 54, h), 1)
        pygame.draw.line(surface, ui.MAGENTA, (0, horizon), (width, horizon), 2)

    def draw_play(self, surface: pygame.Surface) -> None:
        self._build_rows(surface)
        self._draw_road(surface)
        self._draw_objects(surface)
        self._draw_car(surface)
        self._draw_speed_lines(surface)
        if self.hit_flash > 0.0:
            flash = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            flash.fill((255, 60, 60, int(110 * self.hit_flash)))
            surface.blit(flash, (0, 0))

    def _draw_road(self, surface: pygame.Surface) -> None:
        rows = self.road_rows
        if len(rows) < 2:
            return
        shake_x, shake_y = self.shake.offset
        width = surface.get_width()
        far = rows[-1][3]

        def quad(left0, right0, y0, left1, right1, y1, colour):
            pygame.draw.polygon(surface, colour, [
                (left0 + shake_x, y0 + shake_y), (right0 + shake_x, y0 + shake_y),
                (right1 + shake_x, y1 + shake_y), (left1 + shake_x, y1 + shake_y)])

        for i in range(len(rows) - 1):
            y0, c0, w0, d0 = rows[i]
            y1, c1, w1, _ = rows[i + 1]
            z = self.distance + d0
            stripe = int(z / 12.0) % 2 == 0
            # Distance fog: strips fade into the skyline instead of stopping dead.
            fog = min(1.0, d0 / max(1.0, far))
            tarmac = ui.lerp_color((26, 26, 48) if stripe else (19, 19, 38), (32, 12, 46), fog)
            verge = ui.lerp_color((15, 9, 34) if stripe else (11, 7, 27), (30, 10, 44), fog)
            pygame.draw.rect(surface, verge, (0, y1 + shake_y, width, y0 - y1 + 2))
            quad(c0 - w0, c0 + w0, y0, c1 - w1, c1 + w1, y1, tarmac)

            # Kerbs: alternating neon blocks read as speed.
            kerb = w0 * 0.055
            kerb_colour = ui.lerp_color(ui.MAGENTA if stripe else ui.CYAN, (40, 16, 56), fog * 0.8)
            quad(c0 - w0 - kerb, c0 - w0, y0, c1 - w1 - kerb, c1 - w1, y1, kerb_colour)
            quad(c0 + w0, c0 + w0 + kerb, y0, c1 + w1, c1 + w1 + kerb, y1, kerb_colour)

            if stripe and w0 > 14:
                lane = max(1.0, w0 * 0.012)
                lane_colour = ui.lerp_color((170, 172, 210), (40, 20, 60), fog)
                for lane_x in (-0.34, 0.34):
                    quad(c0 + lane_x * w0 - lane, c0 + lane_x * w0 + lane, y0,
                         c1 + lane_x * w1 - lane, c1 + lane_x * w1 + lane, y1, lane_colour)
            if int(z / 40.0) % 2 == 0 and stripe and w0 > 30:
                for side in (-1.28, 1.28):
                    ui.draw_glow_circle(surface, (int(c0 + side * w0 + shake_x), int(y0 + shake_y)),
                                        max(2, min(12, w0 * 0.05)), ui.VIOLET, layers=2)

    def _draw_objects(self, surface: pygame.Surface) -> None:
        shake_x, shake_y = self.shake.offset
        for obj in sorted(self.objects, key=lambda o: -(o.z - self.distance)):
            projected = self._row_for_distance(obj.z - self.distance)
            if projected is None:
                continue
            y, centre, half_w = projected
            x = centre + obj.x * half_w
            size = max(3.0, min(half_w * obj.width, self.size[1] * 0.13))
            px, py = int(x + shake_x), int(y + shake_y)
            if obj.kind == "pickup":
                bob = math.sin(self.time * 6.0 + obj.z) * size * 0.3
                ui.draw_glow_circle(surface, (px, int(py + bob)), size * 0.55, obj.color, layers=2)
                if size > 12:
                    ui.draw_text(surface, obj.powerup[0], (px, py + bob), int(size), ui.BG,
                                 align="center", bold=True)
            elif obj.kind == "hazard":
                points = [(px, py - size), (px + size, py), (px, py + size * 0.4), (px - size, py)]
                pygame.draw.polygon(surface, obj.color, points)
                pygame.draw.polygon(surface, ui.WHITE, points, 1)
            else:
                rect = pygame.Rect(0, 0, int(size * 2), int(size * 1.5))
                rect.midbottom = (px, py)
                pygame.draw.rect(surface, tuple(c // 3 for c in obj.color), rect.inflate(6, 6), border_radius=4)
                pygame.draw.rect(surface, obj.color, rect, border_radius=4)
                pygame.draw.rect(surface, ui.WHITE, rect, 1, border_radius=4)
                if size > 10:
                    pygame.draw.rect(surface, ui.RED, (rect.x, rect.bottom - 4, rect.width, 3))

    def _draw_car(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        shake_x, shake_y = self.shake.offset
        base_y = height * 0.88 + shake_y
        lean = self.player_vx * 0.06
        car_w = width * 0.085
        car_h = car_w * 0.62
        x = width * 0.5 + shake_x  # the camera tracks the car, so it stays centred
        if self.invulnerable > 0 and int(self.time * 14) % 2 == 0:
            body = ui.WHITE
        elif self.ghost_timer > 0:
            body = ui.VIOLET
        else:
            body = ui.CYAN
        points = [
            (x - car_w * (0.55 - lean), base_y),
            (x + car_w * (0.55 + lean), base_y),
            (x + car_w * (0.34 + lean * 1.6), base_y - car_h),
            (x - car_w * (0.34 - lean * 1.6), base_y - car_h),
        ]
        shadow = [(px, py + 6) for px, py in points]
        pygame.draw.polygon(surface, (0, 0, 0), shadow)
        pygame.draw.polygon(surface, tuple(c // 4 for c in body), points)
        pygame.draw.polygon(surface, body, points, 3)
        pygame.draw.polygon(surface, ui.WHITE, [
            (x - car_w * 0.22, base_y - car_h * 0.35),
            (x + car_w * 0.22, base_y - car_h * 0.35),
            (x + car_w * 0.16, base_y - car_h * 0.8),
            (x - car_w * 0.16, base_y - car_h * 0.8),
        ], 2)
        glow = ui.AMBER if (self.boosting or self.nitro_timer > 0) else ui.MAGENTA
        flame = car_w * (0.5 if (self.boosting or self.nitro_timer > 0) else 0.22)
        for side in (-0.32, 0.32):
            ui.draw_glow_circle(surface, (int(x + side * car_w), int(base_y + 4)), flame * 0.5, glow, layers=2)
        if self.drifting:
            for side in (-0.5, 0.5):
                self.particles.trail((x + side * car_w, base_y), ui.WHITE, count=1, spread=70, life=0.4, size=3)

    def _draw_speed_lines(self, surface: pygame.Surface) -> None:
        intensity = clamp((self.speed - MIN_SPEED) / (BOOST_SPEED - MIN_SPEED), 0.0, 1.0)
        color = ui.AMBER if self.boosting else ui.CYAN
        for x, y, life in self.speed_lines:
            length = 30 + 90 * intensity
            alpha_color = tuple(int(c * min(1.0, life * 3)) for c in color)
            pygame.draw.line(surface, alpha_color, (x, y), (x, y + length), 2)

    # ---------------------------------------------------------------- HUD

    def draw_hud(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        self.draw_default_hud(surface)

        # Speed + throttle
        speed_kph = int(self.speed * 1.15)
        ui.draw_text(surface, f"{speed_kph:3d}", (width - 24, height - 74), 54, ui.AMBER,
                     align="bottomright", bold=True, glow=0.6)
        ui.draw_text(surface, "KM/H", (width - 24, height - 52), 18, ui.TEXT_DIM, align="bottomright")

        bar = pygame.Rect(width - 250, height - 42, 226, 16)
        ui.draw_bar(surface, bar, self.speed / BOOST_SPEED, ui.AMBER)

        boost_rect = pygame.Rect(24, height - 42, 240, 16)
        ui.draw_text(surface, "BOOST", (24, height - 50), 16, ui.TEXT_DIM, align="bottomleft")
        ui.draw_bar(surface, boost_rect, self.boost_meter, ui.CYAN if self.boost_meter > 0.2 else ui.RED,
                    segments=6)

        # Damage pips
        for i in range(MAX_DAMAGE):
            colour = ui.RED if i < self.damage else ui.LIME
            pygame.draw.circle(surface, colour, (34 + i * 26, height - 70), 8)
            pygame.draw.circle(surface, ui.BG, (34 + i * 26, height - 70), 8, 2)

        if self.combo > 1.0:
            ui.draw_text(surface, f"COMBO x{self.combo:.1f}", (width // 2, 26), 30, ui.LIME,
                         align="center", bold=True, glow=ui.pulse(self.time, 8.0))
        if self.powerup:
            rect = pygame.Rect(width // 2 - 110, height - 62, 220, 34)
            ui.draw_panel(surface, rect, border=ui.LIME, alpha=180)
            ui.draw_text(surface, f"[B3] {self.powerup}", rect.center, 20, ui.LIME, align="center", bold=True)
        for label, timer, color in (("SHIELD", self.invulnerable, ui.CYAN),
                                    ("GHOST", self.ghost_timer, ui.VIOLET),
                                    ("NITRO", self.nitro_timer, ui.AMBER)):
            if timer > 0.9:
                ui.draw_text(surface, f"{label} {timer:.0f}s", (width // 2, 62), 20, color,
                             align="center", bold=True)
                break

    def result_lines(self):
        return [
            (f"DISTANCE {int(self.distance / 10):,} m", ui.CYAN),
            (f"TOP COMBO x{self.best_combo:.1f}", ui.LIME),
        ]
