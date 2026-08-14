"""ORBITAL DEFENDER - orbital turret defends a space station.

POT 1 slides the turret around the orbit ring, POT 2 swings the aim.
B1 fires, B2 raises the shield, B3 launches a homing missile, B4 fires an EMP.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import List, Tuple

import pygame

from arcade import ui
from arcade.effects import Starfield
from arcade.game import BaseGame, approach, clamp

TAU = math.tau

STATION_HP = 100.0
SHIELD_MAX = 100.0
SHIELD_DRAIN = 34.0
SHIELD_REGEN = 13.0
FIRE_INTERVAL = 0.14
BULLET_SPEED = 720.0
MISSILE_CHARGES = 3
EMP_CHARGES = 2
COMBO_WINDOW = 2.2


@dataclass
class Bullet:
    x: float
    y: float
    vx: float
    vy: float
    life: float = 1.6
    color: Tuple[int, int, int] = ui.CYAN
    damage: float = 1.0
    radius: float = 4.0
    homing: bool = False
    blast: float = 0.0


@dataclass
class Enemy:
    angle: float          # spawn bearing from the station
    dist: float           # distance from station centre
    speed: float
    hp: float
    max_hp: float
    kind: str             # "asteroid" | "drone" | "boss"
    radius: float
    spin: float = 0.0
    value: int = 100
    wobble: float = 0.0
    flash: float = 0.0
    fire_timer: float = 2.0
    vertices: List[float] = field(default_factory=list)

    def position(self, centre) -> Tuple[float, float]:
        angle = self.angle + math.sin(self.wobble) * 0.12
        return (centre[0] + math.cos(angle) * self.dist, centre[1] + math.sin(angle) * self.dist)


class OrbitalDefender(BaseGame):
    game_id = "orbital_defender"
    title = "ORBITAL DEFENDER"
    subtitle = "HOLD THE STATION"
    accent = ui.CYAN
    control_hints = (
        ("POT 1", "ORBIT AROUND STATION"),
        ("POT 2", "AIM WEAPON"),
        ("BUTTON 1", "FIRE"),
        ("BUTTON 2", "SHIELD"),
        ("BUTTON 3", "MISSILE"),
        ("BUTTON 4", "EMP BLAST"),
    )

    def __init__(self, app):
        super().__init__(app)
        self.stars = Starfield(app.screen.get_size(), count=110, speed=12.0)
        self.reset_game()

    def on_resize(self, size) -> None:
        super().on_resize(size)
        self.stars.resize(size)

    # -------------------------------------------------------------- state

    def reset_game(self) -> None:
        self.score = 0
        self.hp = STATION_HP
        self.shield = SHIELD_MAX
        self.shield_up = False
        self.turret_angle = -math.pi / 2
        self.aim_offset = 0.0
        self.fire_timer = 0.0
        self.recoil = 0.0
        self.bullets: List[Bullet] = []
        self.enemies: List[Enemy] = []
        self.enemy_shots: List[Bullet] = []
        self.missiles = MISSILE_CHARGES
        self.emps = EMP_CHARGES
        self.wave = 0
        self.wave_timer = 2.0
        self.wave_banner = 0.0
        self.spawn_queue = 0
        self.spawn_timer = 0.0
        self.combo = 0
        self.combo_timer = 0.0
        self.best_combo = 0
        self.kills = 0
        self.emp_flash = 0.0
        self.hit_flash = 0.0
        self.boss_active = False

    # ------------------------------------------------------------ geometry

    @property
    def centre(self) -> Tuple[float, float]:
        return (self.size[0] * 0.5, self.size[1] * 0.52)

    @property
    def orbit_radius(self) -> float:
        return min(self.size) * 0.21

    @property
    def station_radius(self) -> float:
        return min(self.size) * 0.075

    def turret_pos(self) -> Tuple[float, float]:
        cx, cy = self.centre
        radius = self.orbit_radius - self.recoil * 10.0
        return (cx + math.cos(self.turret_angle) * radius, cy + math.sin(self.turret_angle) * radius)

    def aim_angle(self) -> float:
        return self.turret_angle + self.aim_offset

    # ----------------------------------------------------------- gameplay

    def _start_wave(self) -> None:
        self.wave += 1
        self.boss_active = False
        base = 4 + self.wave
        self.spawn_queue = base
        self.spawn_timer = 0.0
        self.wave_banner = 2.2
        self.app.audio.play("warning")
        if self.wave % 4 == 0:
            self._spawn_boss()

    def _spawn_boss(self) -> None:
        hp = 34 + self.wave * 9
        self.boss_active = True
        self.enemies.append(
            Enemy(random.uniform(0, TAU), max(self.size) * 0.65, 44.0 + self.wave * 1.5, hp, hp,
                  "boss", min(self.size) * 0.075, value=1500,
                  vertices=[random.uniform(0.78, 1.2) for _ in range(11)])
        )
        self.floaters.add("WARNING - HEAVY DRONE", (self.size[0] * 0.5, self.size[1] * 0.3), ui.RED, 34, 2.0)

    def _spawn_enemy(self) -> None:
        difficulty = 1.0 + self.wave * 0.11
        drone = random.random() < min(0.55, 0.18 + self.wave * 0.05)
        radius = min(self.size) * (0.02 if drone else random.uniform(0.018, 0.033))
        hp = (2 if drone else 1) + self.wave // 3
        self.enemies.append(
            Enemy(
                random.uniform(0, TAU),
                max(self.size) * 0.62,
                (104 if drone else 82) * difficulty * random.uniform(0.85, 1.2),
                hp, hp,
                "drone" if drone else "asteroid",
                radius,
                spin=random.uniform(-2.5, 2.5),
                value=180 if drone else 100,
                vertices=[random.uniform(0.7, 1.25) for _ in range(9)],
            )
        )

    def update_play(self, dt: float, controller) -> None:
        self.stars.update(dt, 0.4)
        self.hit_flash = max(0.0, self.hit_flash - dt * 2.4)
        self.emp_flash = max(0.0, self.emp_flash - dt * 1.8)
        self.recoil = max(0.0, self.recoil - dt * 5.0)

        # --- direct analog control ----------------------------------------
        # Pot 1 is an absolute orbital position: turning the knob physically
        # slides the turret around the ring.
        target_angle = -math.pi / 2 + (controller.pot1 - 0.5) * TAU
        self.turret_angle = approach(self.turret_angle, target_angle, 16.0, dt)
        self.aim_offset = approach(self.aim_offset, (controller.pot2 - 0.5) * math.pi * 1.15, 18.0, dt)

        # --- weapons -------------------------------------------------------
        self.fire_timer = max(0.0, self.fire_timer - dt)
        if controller.button1 and self.fire_timer <= 0.0:
            self._fire()
        if controller.button_pressed(3):
            self._launch_missile()
        if controller.button_pressed(4):
            self._fire_emp()

        # --- shield --------------------------------------------------------
        self.shield_up = controller.button2 and self.shield > 1.0
        if self.shield_up:
            self.shield = max(0.0, self.shield - SHIELD_DRAIN * dt)
        else:
            self.shield = min(SHIELD_MAX, self.shield + SHIELD_REGEN * dt)

        # --- combo ---------------------------------------------------------
        if self.combo_timer > 0.0:
            self.combo_timer -= dt
            if self.combo_timer <= 0.0:
                self.combo = 0

        self._update_waves(dt)
        self._update_bullets(dt)
        self._update_enemies(dt)
        self.wave_banner = max(0.0, self.wave_banner - dt)

        if self.hp <= 0:
            self.game_over("STATION LOST")

    def _update_waves(self, dt: float) -> None:
        if self.spawn_queue > 0:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0.0:
                self._spawn_enemy()
                self.spawn_queue -= 1
                self.spawn_timer = max(0.22, 0.9 - self.wave * 0.04)
        elif not self.enemies:
            self.wave_timer -= dt
            if self.wave_timer <= 0.0:
                self.wave_timer = 2.6
                if self.wave > 0:
                    bonus = 500 * self.wave
                    self.score += bonus
                    self.floaters.add(f"WAVE CLEAR  +{bonus}", (self.size[0] * 0.5, self.size[1] * 0.36),
                                      ui.LIME, 34, 1.6)
                    self.missiles = min(MISSILE_CHARGES, self.missiles + 1)
                    self.hp = min(STATION_HP, self.hp + 8)
                    self.app.audio.play("success")
                self._start_wave()

    def _fire(self) -> None:
        self.fire_timer = FIRE_INTERVAL
        angle = self.aim_angle()
        x, y = self.turret_pos()
        muzzle = (x + math.cos(angle) * 26, y + math.sin(angle) * 26)
        self.bullets.append(Bullet(muzzle[0], muzzle[1],
                                   math.cos(angle) * BULLET_SPEED, math.sin(angle) * BULLET_SPEED))
        self.recoil = 1.0
        self.app.audio.play("shoot", 0.5)
        self.particles.burst(muzzle, 4, ui.CYAN, speed=160, life=0.2, spread=0.7, direction=angle, size=2)

    def _launch_missile(self) -> None:
        if self.missiles <= 0:
            self.app.audio.play("fail", 0.4)
            return
        self.missiles -= 1
        angle = self.aim_angle()
        x, y = self.turret_pos()
        self.bullets.append(Bullet(x, y, math.cos(angle) * 320, math.sin(angle) * 320,
                                   life=3.0, color=ui.AMBER, damage=6.0, radius=7.0,
                                   homing=True, blast=90.0))
        self.app.audio.play("missile")
        self.shake.add(4.0)

    def _fire_emp(self) -> None:
        if self.emps <= 0:
            self.app.audio.play("fail", 0.4)
            return
        self.emps -= 1
        self.emp_flash = 1.0
        self.app.audio.play("emp")
        self.shake.add(12.0)
        centre = self.centre
        reach = min(self.size) * 0.46
        for enemy in list(self.enemies):
            ex, ey = enemy.position(centre)
            if math.hypot(ex - centre[0], ey - centre[1]) < reach:
                enemy.hp -= 4
                enemy.flash = 0.4
                enemy.speed *= 0.55
                if enemy.hp <= 0:
                    self._kill(enemy)
        self.enemy_shots.clear()
        self.floaters.add("EMP!", (self.size[0] * 0.5, self.size[1] * 0.42), ui.VIOLET, 44, 1.0)

    def _update_bullets(self, dt: float) -> None:
        width, height = self.size
        centre = self.centre
        alive = []
        for bullet in self.bullets:
            bullet.life -= dt
            if bullet.homing:
                target = self._nearest_enemy((bullet.x, bullet.y))
                if target is not None:
                    tx, ty = target.position(centre)
                    desired = math.atan2(ty - bullet.y, tx - bullet.x)
                    current = math.atan2(bullet.vy, bullet.vx)
                    delta = (desired - current + math.pi) % TAU - math.pi
                    current += clamp(delta, -3.4 * dt, 3.4 * dt)
                    speed = math.hypot(bullet.vx, bullet.vy)
                    bullet.vx, bullet.vy = math.cos(current) * speed, math.sin(current) * speed
                self.particles.trail((bullet.x, bullet.y), ui.AMBER, count=1, spread=30, life=0.3, size=3)
            bullet.x += bullet.vx * dt
            bullet.y += bullet.vy * dt
            if bullet.life <= 0 or not (-60 < bullet.x < width + 60 and -60 < bullet.y < height + 60):
                continue
            if not self._bullet_hits(bullet):
                alive.append(bullet)
        self.bullets = alive

        remaining = []
        for shot in self.enemy_shots:
            shot.life -= dt
            shot.x += shot.vx * dt
            shot.y += shot.vy * dt
            if shot.life <= 0:
                continue
            distance = math.hypot(shot.x - centre[0], shot.y - centre[1])
            if distance < self.station_radius + 6:
                self._damage_station(6.0, (shot.x, shot.y))
                continue
            if self.shield_up and abs(distance - self.orbit_radius) < 14:
                self.particles.burst((shot.x, shot.y), 8, ui.CYAN, speed=200, life=0.35)
                self.app.audio.play("shield", 0.4)
                continue
            remaining.append(shot)
        self.enemy_shots = remaining

    def _nearest_enemy(self, pos):
        centre = self.centre
        best, best_d = None, 1e9
        for enemy in self.enemies:
            ex, ey = enemy.position(centre)
            d = math.hypot(ex - pos[0], ey - pos[1])
            if d < best_d:
                best, best_d = enemy, d
        return best

    def _bullet_hits(self, bullet: Bullet) -> bool:
        centre = self.centre
        for enemy in self.enemies:
            ex, ey = enemy.position(centre)
            if math.hypot(ex - bullet.x, ey - bullet.y) < enemy.radius + bullet.radius:
                enemy.hp -= bullet.damage
                enemy.flash = 0.25
                self.app.audio.play("hit", 0.45)
                self.particles.burst((bullet.x, bullet.y), 8, ui.WHITE, speed=220, life=0.3, size=2.5, kind="spark")
                if bullet.blast > 0.0:
                    self._explode(bullet.x, bullet.y, bullet.blast)
                if enemy.hp <= 0:
                    self._kill(enemy)
                return True
        return False

    def _explode(self, x: float, y: float, radius: float) -> None:
        centre = self.centre
        self.particles.burst((x, y), 30, ui.AMBER, speed=420, life=0.6, size=4)
        self.shake.add(9.0)
        self.app.audio.play("explosion", 0.7)
        for enemy in list(self.enemies):
            ex, ey = enemy.position(centre)
            if math.hypot(ex - x, ey - y) < radius:
                enemy.hp -= 4
                enemy.flash = 0.3
                if enemy.hp <= 0:
                    self._kill(enemy)

    def _kill(self, enemy: Enemy) -> None:
        if enemy not in self.enemies:
            return
        self.enemies.remove(enemy)
        self.kills += 1
        self.combo += 1
        self.best_combo = max(self.best_combo, self.combo)
        self.combo_timer = COMBO_WINDOW
        multiplier = 1.0 + self.combo * 0.1
        gain = int(enemy.value * multiplier)
        self.score += gain
        pos = enemy.position(self.centre)
        colour = ui.RED if enemy.kind == "boss" else (ui.MAGENTA if enemy.kind == "drone" else ui.AMBER)
        self.particles.burst(pos, 26 if enemy.kind != "boss" else 60, colour,
                             speed=340, life=0.65, size=3.5)
        self.app.audio.play("explosion" if enemy.kind == "boss" else "hit", 0.8)
        self.shake.add(10.0 if enemy.kind == "boss" else 2.5)
        if self.combo >= 3:
            self.floaters.add(f"x{self.combo} COMBO  +{gain}", pos, ui.LIME, 24, 0.8)
        if enemy.kind == "boss":
            self.boss_active = False
            self.emps = min(EMP_CHARGES, self.emps + 1)
            self.floaters.add("HEAVY DRONE DOWN!", (self.size[0] * 0.5, self.size[1] * 0.35), ui.LIME, 36, 1.8)

    def _update_enemies(self, dt: float) -> None:
        centre = self.centre
        for enemy in list(self.enemies):
            enemy.flash = max(0.0, enemy.flash - dt)
            enemy.wobble += dt * 1.6
            enemy.dist -= enemy.speed * dt
            if enemy.kind in ("drone", "boss"):
                enemy.angle += dt * (0.25 if enemy.kind == "drone" else 0.4) * math.sin(enemy.wobble * 0.4)
                enemy.fire_timer -= dt
                if enemy.fire_timer <= 0.0 and enemy.dist < min(self.size) * 0.55:
                    enemy.fire_timer = random.uniform(1.6, 3.2)
                    ex, ey = enemy.position(centre)
                    angle = math.atan2(centre[1] - ey, centre[0] - ex)
                    self.enemy_shots.append(
                        Bullet(ex, ey, math.cos(angle) * 260, math.sin(angle) * 260,
                               life=4.0, color=ui.RED, radius=5.0)
                    )
            # Shield ring blocks anything that touches the orbit.
            if self.shield_up and abs(enemy.dist - self.orbit_radius) < enemy.radius + 8:
                enemy.hp -= 8 * dt * 6
                enemy.flash = 0.3
                self.particles.burst(enemy.position(centre), 4, ui.CYAN, speed=160, life=0.3)
                if enemy.hp <= 0:
                    self._kill(enemy)
                    continue
            if enemy.dist <= self.station_radius + enemy.radius * 0.5:
                damage = 26 if enemy.kind == "boss" else (10 if enemy.kind == "drone" else 7)
                self._damage_station(damage, enemy.position(centre))
                self.enemies.remove(enemy)

    def _damage_station(self, amount: float, pos) -> None:
        if self.shield_up:
            self.shield = max(0.0, self.shield - amount * 1.6)
            self.app.audio.play("shield", 0.6)
            self.particles.burst(pos, 12, ui.CYAN, speed=240, life=0.4)
            return
        self.hp -= amount
        self.combo = 0
        self.hit_flash = 1.0
        self.shake.add(12.0)
        self.app.audio.play("collision", 0.8)
        self.particles.burst(pos, 20, ui.RED, speed=280, life=0.5)
        if self.hp <= 0:
            self.hp = 0

    # ------------------------------------------------------------- render

    def draw_background(self, surface: pygame.Surface) -> None:
        surface.fill(ui.BG_DEEP)
        self.stars.draw(surface)

    def draw_play(self, surface: pygame.Surface) -> None:
        shake = self.shake.offset
        centre = (self.centre[0] + shake[0], self.centre[1] + shake[1])
        self._draw_orbit_ring(surface, centre)
        self._draw_station(surface, centre)
        self._draw_enemies(surface, centre)
        self._draw_bullets(surface, shake)
        self._draw_turret(surface, centre)
        if self.emp_flash > 0.0:
            radius = int(min(self.size) * 0.5 * (1.0 - self.emp_flash))
            pygame.draw.circle(surface, ui.VIOLET, (int(centre[0]), int(centre[1])), max(2, radius),
                               max(2, int(14 * self.emp_flash)))
        if self.hit_flash > 0.0:
            flash = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            flash.fill((255, 40, 40, int(90 * self.hit_flash)))
            surface.blit(flash, (0, 0))

    def _draw_orbit_ring(self, surface, centre) -> None:
        radius = int(self.orbit_radius)
        colour = ui.CYAN if not self.shield_up else ui.LIME
        pygame.draw.circle(surface, tuple(c // 4 for c in colour), (int(centre[0]), int(centre[1])), radius, 2)
        if self.shield_up:
            alpha = int(70 + 60 * ui.pulse(self.time, 12))
            shield = pygame.Surface((radius * 2 + 20, radius * 2 + 20), pygame.SRCALPHA)
            pygame.draw.circle(shield, (*ui.LIME, alpha), (radius + 10, radius + 10), radius, 10)
            surface.blit(shield, (centre[0] - radius - 10, centre[1] - radius - 10))
        for i in range(24):
            angle = i / 24.0 * TAU
            x = centre[0] + math.cos(angle) * radius
            y = centre[1] + math.sin(angle) * radius
            pygame.draw.circle(surface, tuple(c // 3 for c in colour), (int(x), int(y)), 2)

    def _draw_station(self, surface, centre) -> None:
        radius = self.station_radius
        health = self.hp / STATION_HP
        colour = ui.lerp_color(ui.RED, ui.CYAN, health)
        ui.draw_glow_circle(surface, (int(centre[0]), int(centre[1])), radius * 0.75, colour, layers=3)
        pygame.draw.circle(surface, ui.BG, (int(centre[0]), int(centre[1])), int(radius))
        pygame.draw.circle(surface, colour, (int(centre[0]), int(centre[1])), int(radius), 3)
        for i in range(6):
            angle = self.time * 0.4 + i * TAU / 6
            x = centre[0] + math.cos(angle) * radius * 0.62
            y = centre[1] + math.sin(angle) * radius * 0.62
            pygame.draw.circle(surface, colour, (int(x), int(y)), max(2, int(radius * 0.11)))
        arc_rect = pygame.Rect(0, 0, int(radius * 2.4), int(radius * 2.4))
        arc_rect.center = (int(centre[0]), int(centre[1]))
        pygame.draw.arc(surface, ui.LIME, arc_rect, -math.pi / 2, -math.pi / 2 + TAU * health, 4)

    def _draw_turret(self, surface, centre) -> None:
        angle = self.aim_angle()
        radius = self.orbit_radius - self.recoil * 10.0
        x = centre[0] + math.cos(self.turret_angle) * radius
        y = centre[1] + math.sin(self.turret_angle) * radius
        # Aim beam makes the pot-2 position unmistakable.
        far = (x + math.cos(angle) * min(self.size) * 0.55, y + math.sin(angle) * min(self.size) * 0.55)
        pygame.draw.line(surface, tuple(c // 4 for c in ui.CYAN), (x, y), far, 1)
        ui.draw_glow_line(surface, (x, y), (x + math.cos(angle) * 40, y + math.sin(angle) * 40), ui.CYAN, 5)
        body = [
            (x + math.cos(angle + 2.4) * 16, y + math.sin(angle + 2.4) * 16),
            (x + math.cos(angle) * 24, y + math.sin(angle) * 24),
            (x + math.cos(angle - 2.4) * 16, y + math.sin(angle - 2.4) * 16),
        ]
        pygame.draw.polygon(surface, ui.BG, body)
        pygame.draw.polygon(surface, ui.LIME if self.shield_up else ui.CYAN, body, 3)
        ui.draw_glow_circle(surface, (int(x), int(y)), 7, ui.WHITE, layers=2)

    def _draw_enemies(self, surface, centre) -> None:
        for enemy in self.enemies:
            x, y = enemy.position(centre)
            colour = ui.RED if enemy.kind == "boss" else (ui.MAGENTA if enemy.kind == "drone" else ui.AMBER)
            if enemy.flash > 0:
                colour = ui.WHITE
            points = []
            count = len(enemy.vertices) or 8
            for i in range(count):
                angle = i / count * TAU + self.time * enemy.spin
                scale = enemy.vertices[i] if enemy.vertices else 1.0
                points.append((x + math.cos(angle) * enemy.radius * scale,
                               y + math.sin(angle) * enemy.radius * scale))
            pygame.draw.polygon(surface, tuple(c // 4 for c in colour), points)
            pygame.draw.polygon(surface, colour, points, 2)
            if enemy.kind == "boss":
                bar = pygame.Rect(int(x - enemy.radius), int(y - enemy.radius - 16), int(enemy.radius * 2), 7)
                ui.draw_bar(surface, bar, max(0.0, enemy.hp / enemy.max_hp), ui.RED, radius=3)
            elif enemy.kind == "drone":
                pygame.draw.circle(surface, ui.WHITE, (int(x), int(y)), max(2, int(enemy.radius * 0.3)))

    def _draw_bullets(self, surface, shake) -> None:
        for bullet in self.bullets:
            pos = (int(bullet.x + shake[0]), int(bullet.y + shake[1]))
            ui.draw_glow_circle(surface, pos, bullet.radius, bullet.color, layers=2)
        for shot in self.enemy_shots:
            pos = (int(shot.x + shake[0]), int(shot.y + shake[1]))
            ui.draw_glow_circle(surface, pos, shot.radius, ui.RED, layers=2)

    # ---------------------------------------------------------------- HUD

    def draw_hud(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        self.draw_default_hud(surface)

        ui.draw_text(surface, f"WAVE {self.wave}", (width // 2, 24), 28, ui.VIOLET,
                     align="midtop", bold=True, glow=0.4)

        ui.draw_text(surface, "HULL", (24, height - 112), 16, ui.TEXT_DIM)
        hull = pygame.Rect(24, height - 92, 250, 18)
        ui.draw_bar(surface, hull, self.hp / STATION_HP, ui.lerp_color(ui.RED, ui.LIME, self.hp / STATION_HP))

        ui.draw_text(surface, "SHIELD [B2]", (24, height - 62), 16, ui.TEXT_DIM)
        shield = pygame.Rect(24, height - 42, 250, 18)
        ui.draw_bar(surface, shield, self.shield / SHIELD_MAX, ui.CYAN if not self.shield_up else ui.LIME)

        ui.draw_text(surface, "MISSILE [B3]", (width - 24, height - 112), 15, ui.TEXT_DIM, align="topright")
        for i in range(MISSILE_CHARGES):
            colour = ui.AMBER if i < self.missiles else (40, 40, 60)
            pygame.draw.polygon(surface, colour, [
                (width - 40 - i * 26, height - 90), (width - 32 - i * 26, height - 74),
                (width - 48 - i * 26, height - 74)])
        ui.draw_text(surface, "EMP [B4]", (width - 24, height - 62), 15, ui.TEXT_DIM, align="topright")
        for i in range(EMP_CHARGES):
            colour = ui.VIOLET if i < self.emps else (40, 40, 60)
            pygame.draw.circle(surface, colour, (width - 36 - i * 26, height - 32), 8)

        # Physical knob mirrors: the on-screen dials match the real ones.
        self._draw_knob(surface, (width - 76, 96), self.turret_angle, "POT 1  ORBIT", ui.CYAN)
        self._draw_knob(surface, (width - 76, 190), self.aim_offset - math.pi / 2, "POT 2  AIM", ui.MAGENTA)

        if self.combo >= 3:
            ui.draw_text(surface, f"COMBO x{self.combo}", (width // 2, 60), 26, ui.LIME,
                         align="center", bold=True, glow=ui.pulse(self.time, 9))
        if self.wave_banner > 0.0:
            alpha = int(255 * min(1.0, self.wave_banner / 0.6))
            ui.draw_text(surface, f"WAVE {self.wave}", (width // 2, height * 0.34), 60, ui.VIOLET,
                         align="center", bold=True, glow=1.0, alpha=alpha)
            if self.boss_active:
                ui.draw_text(surface, "HEAVY DRONE INBOUND", (width // 2, height * 0.42), 26, ui.RED,
                             align="center", bold=True, alpha=alpha)

    def _draw_knob(self, surface, pos, angle: float, label: str, colour) -> None:
        pygame.draw.circle(surface, ui.PANEL, pos, 26)
        pygame.draw.circle(surface, colour, pos, 26, 2)
        tip = (pos[0] + math.cos(angle) * 20, pos[1] + math.sin(angle) * 20)
        pygame.draw.line(surface, colour, pos, tip, 3)
        ui.draw_text(surface, label, (pos[0], pos[1] + 32), 14, ui.TEXT_DIM, align="center")

    def result_lines(self):
        return [
            (f"WAVES SURVIVED {max(0, self.wave - 1)}", ui.VIOLET),
            (f"KILLS {self.kills}   BEST COMBO x{self.best_combo}", ui.LIME),
        ]
