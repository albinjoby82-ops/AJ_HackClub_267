"""REACTOR SYNC - keep an unstable reactor alive with two knobs and four buttons.

POT 1 tunes channel A, POT 2 tunes channel B: hold both inside their moving
safe zones.  Alarms demand a specific button - B1 locks A, B2 vents coolant,
B3 locks B, B4 dumps the core charge.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import pygame

from arcade import ui
from arcade.game import BaseGame, approach, clamp

STABILITY_MAX = 100.0
LOCK_TIME = 2.6
LOCK_COOLDOWN = 5.0
ALARM_BUTTONS = {
    1: ("LOCK CHANNEL A!", ui.CYAN),
    2: ("VENT COOLANT!", ui.LIME),
    3: ("LOCK CHANNEL B!", ui.MAGENTA),
    4: ("DISCHARGE CORE!", ui.AMBER),
}


@dataclass
class Channel:
    label: str
    colour: Tuple[int, int, int]
    value: float = 0.5
    target: float = 0.5
    velocity: float = 0.11
    zone: float = 0.17
    locked: float = 0.0
    cooldown: float = 0.0
    inverted: float = 0.0
    phase: float = 0.0
    in_zone: bool = False
    time_in_zone: float = 0.0

    @property
    def error(self) -> float:
        return abs(self.value - self.target)

    def update_target(self, dt: float, difficulty: float) -> None:
        self.target += self.velocity * dt
        if self.target > 1.0:
            self.target, self.velocity = 1.0, -abs(self.velocity)
        elif self.target < 0.0:
            self.target, self.velocity = 0.0, abs(self.velocity)
        if random.random() < 0.35 * dt:
            self.velocity = random.uniform(0.07, 0.15 + 0.3 * difficulty) * random.choice((-1, 1))
        self.zone = max(0.055, 0.17 - 0.1 * difficulty)


@dataclass
class Alarm:
    button: int
    label: str
    colour: Tuple[int, int, int]
    time_left: float
    duration: float


@dataclass
class Event:
    name: str
    time_left: float
    colour: Tuple[int, int, int] = ui.RED
    data: dict = field(default_factory=dict)


class ReactorSync(BaseGame):
    game_id = "reactor_sync"
    title = "REACTOR SYNC"
    subtitle = "STABILISE THE CORE"
    accent = ui.LIME
    control_hints = (
        ("POT 1", "TUNE CHANNEL A"),
        ("POT 2", "TUNE CHANNEL B"),
        ("BUTTON 1", "LOCK CHANNEL A"),
        ("BUTTON 2", "VENT COOLANT"),
        ("BUTTON 3", "LOCK CHANNEL B"),
        ("BUTTON 4", "EMERGENCY DISCHARGE"),
    )

    def __init__(self, app):
        super().__init__(app)
        self.reset_game()

    # -------------------------------------------------------------- state

    def reset_game(self) -> None:
        self.score = 0
        self.stability = STABILITY_MAX
        self.heat = 0.15
        self.charge = 0.0
        self.survived = 0.0
        self.combo = 0
        self.best_combo = 0
        self.channel_a = Channel("CHANNEL A", ui.CYAN)
        self.channel_b = Channel("CHANNEL B", ui.MAGENTA)
        self.alarm: Optional[Alarm] = None
        self.alarm_timer = 4.0
        self.events: List[Event] = []
        self.event_timer = 9.0
        self.flash = 0.0
        self.good_flash = 0.0
        self.alarm_light = 0.0
        self.distortion = 0.0
        self.vent_cooldown = 0.0
        self.last_message = ""
        self.message_timer = 0.0

    @property
    def channels(self):
        return (self.channel_a, self.channel_b)

    @property
    def difficulty(self) -> float:
        return min(1.0, self.survived / 150.0)

    def has_event(self, name: str) -> bool:
        return any(event.name == name for event in self.events)

    # ----------------------------------------------------------- gameplay

    def update_play(self, dt: float, controller) -> None:
        self.survived += dt
        self.flash = max(0.0, self.flash - dt * 2.2)
        self.good_flash = max(0.0, self.good_flash - dt * 3.0)
        self.message_timer = max(0.0, self.message_timer - dt)
        self.vent_cooldown = max(0.0, self.vent_cooldown - dt)
        difficulty = self.difficulty

        self._update_events(dt)
        self._update_channels(dt, controller, difficulty)
        self._update_reactor(dt, controller, difficulty)
        self._update_alarm(dt, controller, difficulty)

        instability = 1.0 - self.stability / STABILITY_MAX
        self.distortion = approach(self.distortion, instability, 3.0, dt)
        self.alarm_light = ui.pulse(self.time, 4.0 + 8.0 * instability)
        if instability > 0.6:
            self.shake.add(instability * 1.4)

        if self.stability <= 0.0:
            self.game_over("MELTDOWN")

    def _update_channels(self, dt: float, controller, difficulty: float) -> None:
        reversed_now = self.has_event("REVERSED")
        for index, channel in enumerate(self.channels, start=1):
            raw = controller.pot(index)
            if reversed_now:
                raw = 1.0 - raw
            channel.cooldown = max(0.0, channel.cooldown - dt)
            if channel.locked > 0.0:
                channel.locked -= dt
                channel.value = approach(channel.value, channel.target, 8.0, dt)
            else:
                channel.value = approach(channel.value, raw, 22.0, dt)
            channel.update_target(dt, difficulty)
            channel.phase += dt * (2.0 + channel.value * 14.0)
            was_in_zone = channel.in_zone
            channel.in_zone = channel.error <= channel.zone or channel.locked > 0.0
            if channel.in_zone:
                channel.time_in_zone += dt
                gain = 22.0 * dt * (1.0 + self.combo * 0.05)
                self.score += gain
                self.stability = min(STABILITY_MAX, self.stability + 5.0 * dt)
                if not was_in_zone:
                    self.app.audio.play("tick", 0.4)
            else:
                channel.time_in_zone = 0.0
                penalty = (5.0 + 9.0 * difficulty) * (channel.error - channel.zone) * 4.0
                self.stability -= penalty * dt
                self.heat = min(1.4, self.heat + 0.055 * dt * (1.0 + channel.error * 3.0))

        # Locks
        if controller.button_pressed(1):
            self._try_lock(self.channel_a, 1)
        if controller.button_pressed(3):
            self._try_lock(self.channel_b, 3)

    def _try_lock(self, channel: Channel, button: int) -> None:
        if self._answer_alarm(button):
            return
        if channel.cooldown > 0.0:
            self.app.audio.play("fail", 0.4)
            self._message(f"{channel.label} LOCK RECHARGING", ui.TEXT_DIM)
            return
        if not channel.in_zone:
            self._penalise(6.0, f"{channel.label} OUT OF SYNC")
            channel.cooldown = LOCK_COOLDOWN * 0.6
            return
        channel.locked = LOCK_TIME
        channel.cooldown = LOCK_COOLDOWN
        self.score += 250
        self._reward(f"{channel.label} LOCKED +250", channel.colour)

    def _update_reactor(self, dt: float, controller, difficulty: float) -> None:
        width, height = self.size
        self.heat = max(0.0, self.heat + (0.018 + 0.05 * difficulty) * dt)
        self.charge = min(1.35, self.charge + (0.035 + 0.055 * difficulty) * dt)

        if controller.button_pressed(2) and not self._answer_alarm(2):
            self._vent(manual=True)
        if controller.button_pressed(4) and not self._answer_alarm(4):
            self._discharge(manual=True)

        if self.heat > 1.0:
            self.stability -= 20.0 * dt * (self.heat - 1.0 + 0.4)
            self.flash = max(self.flash, 0.6)
            if random.random() < 6 * dt:
                self.particles.burst((random.uniform(0, width), height * 0.5), 6, ui.RED,
                                     speed=220, life=0.5)
        if self.charge > 1.0:
            self.stability -= 26.0 * dt
            self.flash = max(self.flash, 0.7)
            if random.random() < 3 * dt:
                self.app.audio.play("alarm", 0.5)

    def _vent(self, manual: bool) -> None:
        width, height = self.size
        if self.vent_cooldown > 0.0 and manual:
            self.app.audio.play("fail", 0.4)
            return
        self.vent_cooldown = 1.6
        cooled = min(self.heat, 0.55)
        self.heat = max(0.0, self.heat - 0.55)
        self.app.audio.play("shield", 0.7)
        self.particles.burst((width * 0.5, height * 0.86), 24, ui.LIME, speed=280, life=0.6)
        if cooled > 0.2:
            self.score += 120
            self._reward("COOLANT VENTED +120", ui.LIME)
        else:
            self._message("COOLANT WASTED", ui.TEXT_DIM)

    def _discharge(self, manual: bool) -> None:
        width, height = self.size
        if self.charge < 0.45 and manual:
            self._penalise(5.0, "CHARGE TOO LOW")
            return
        gain = int(400 * self.charge)
        self.score += gain
        self.charge = 0.0
        self.shake.add(14.0)
        self.app.audio.play("emp")
        self.particles.burst((width * 0.5, height * 0.5), 40, ui.AMBER, speed=460, life=0.8, size=4)
        self._reward(f"CORE DISCHARGED +{gain}", ui.AMBER)

    # -------------------------------------------------------------- alarms

    def _update_alarm(self, dt: float, controller, difficulty: float) -> None:
        if self.alarm is None:
            self.alarm_timer -= dt
            if self.alarm_timer <= 0.0:
                self._raise_alarm(difficulty)
            return
        self.alarm.time_left -= dt
        if self.alarm.time_left <= 0.0:
            failed = self.alarm
            self.alarm = None
            self.alarm_timer = random.uniform(2.5, 4.5)
            self._penalise(14.0, f"MISSED: {failed.label}")

    def _raise_alarm(self, difficulty: float) -> None:
        weights = [1.0, 1.0, 1.0, 1.0]
        if self.heat > 0.6:
            weights[1] += 3.0
        if self.charge > 0.6:
            weights[3] += 3.0
        button = random.choices((1, 2, 3, 4), weights=weights)[0]
        label, colour = ALARM_BUTTONS[button]
        duration = max(1.1, 2.6 - 1.1 * difficulty)
        self.alarm = Alarm(button, label, colour, duration, duration)
        self.app.audio.play("alarm", 0.8)
        self.alarm_timer = random.uniform(3.0, 5.5) * (1.0 - 0.35 * difficulty)

    def _answer_alarm(self, button: int) -> bool:
        """Returns True when the press was consumed by an active alarm."""
        if self.alarm is None:
            return False
        if self.alarm.button != button:
            self._penalise(10.0, "WRONG BUTTON!")
            self.alarm.time_left = min(self.alarm.time_left, 0.6)
            return True
        speed_bonus = int(300 * (self.alarm.time_left / self.alarm.duration))
        gain = 350 + speed_bonus
        self.combo += 1
        self.best_combo = max(self.best_combo, self.combo)
        self.score += gain * (1 + self.combo // 5)
        self.stability = min(STABILITY_MAX, self.stability + 9.0)
        if button == 2:
            self._vent(manual=False)
        elif button == 4:
            self._discharge(manual=False)
        elif button == 1:
            self.channel_a.locked = LOCK_TIME
        else:
            self.channel_b.locked = LOCK_TIME
        self.alarm = None
        self._reward(f"{ALARM_BUTTONS[button][0]} +{gain}", ui.LIME)
        return True

    # -------------------------------------------------------------- events

    def _update_events(self, dt: float) -> None:
        for event in self.events:
            event.time_left -= dt
        self.events = [event for event in self.events if event.time_left > 0]
        self.event_timer -= dt
        if self.event_timer <= 0.0:
            self._trigger_event()

    def _trigger_event(self) -> None:
        difficulty = self.difficulty
        self.event_timer = random.uniform(8.0, 15.0) * (1.0 - 0.35 * difficulty)
        choice = random.choice(("REVERSED", "SURGE", "PRESSURE", "SHRINK", "OVERHEAT"))
        if choice == "REVERSED":
            self.events.append(Event("REVERSED", 6.0, ui.VIOLET))
            self._message("CONTROLS REVERSED!", ui.VIOLET, 2.0)
        elif choice == "SURGE":
            for channel in self.channels:
                channel.target = clamp(channel.target + random.uniform(-0.45, 0.45), 0.0, 1.0)
                channel.velocity *= 1.5
            self.events.append(Event("SURGE", 3.0, ui.AMBER))
            self._message("ELECTRICAL SURGE!", ui.AMBER, 2.0)
            self.shake.add(10.0)
        elif choice == "PRESSURE":
            self.charge = min(1.0, self.charge + 0.45)
            self.events.append(Event("PRESSURE", 4.0, ui.RED))
            self._message("PRESSURE SPIKE!", ui.RED, 2.0)
        elif choice == "SHRINK":
            for channel in self.channels:
                channel.zone = max(0.045, channel.zone * 0.55)
            self.events.append(Event("SHRINK", 6.0, ui.MAGENTA))
            self._message("TOLERANCE NARROWED!", ui.MAGENTA, 2.0)
        else:
            self.heat = min(1.25, self.heat + 0.5)
            self.events.append(Event("OVERHEAT", 5.0, ui.RED))
            self._message("OVERHEATING - VENT!", ui.RED, 2.0)
        self.app.audio.play("warning")

    # ------------------------------------------------------------ feedback

    def _message(self, text: str, colour=ui.TEXT, duration: float = 1.4) -> None:
        self.last_message = text
        self.message_timer = duration
        self.floaters.add(text, (self.size[0] * 0.5, self.size[1] * 0.44), colour, 30, duration)

    def _reward(self, text: str, colour) -> None:
        self.good_flash = 1.0
        self.app.audio.play("success", 0.7)
        self._message(text, colour)

    def _penalise(self, amount: float, text: str) -> None:
        self.stability -= amount
        self.combo = 0
        self.flash = 1.0
        self.shake.add(9.0)
        self.app.audio.play("fail", 0.8)
        self._message(text, ui.RED)

    # -------------------------------------------------------------- render

    def draw_background(self, surface: pygame.Surface) -> None:
        instability = 1.0 - clamp(self.stability / STABILITY_MAX, 0.0, 1.0)
        surface.fill(ui.lerp_color(ui.BG, (46, 6, 10), instability * 0.85))
        width, height = surface.get_size()
        spacing = 48
        colour = ui.lerp_color(ui.GRID, (110, 26, 32), instability)
        offset = int(self.time * 22) % spacing
        for x in range(-spacing, width + spacing, spacing):
            pygame.draw.line(surface, colour, (x + offset, 0), (x + offset, height), 1)
        for y in range(-spacing, height + spacing, spacing):
            pygame.draw.line(surface, colour, (0, y), (width, y), 1)

    def draw_play(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        shake = self.shake.offset
        panel_h = int(height * 0.24)
        for i, channel in enumerate(self.channels):
            rect = pygame.Rect(int(width * 0.06 + shake[0]),
                               int(height * 0.27 + i * (panel_h + height * 0.04) + shake[1]),
                               int(width * 0.62), panel_h)
            self._draw_channel(surface, rect, channel)
        self._draw_core(surface, shake)
        self._draw_gauges(surface)
        if self.flash > 0.0:
            overlay = pygame.Surface((width, height), pygame.SRCALPHA)
            overlay.fill((255, 40, 40, int(80 * self.flash)))
            surface.blit(overlay, (0, 0))
        if self.good_flash > 0.0:
            overlay = pygame.Surface((width, height), pygame.SRCALPHA)
            overlay.fill((120, 255, 140, int(40 * self.good_flash)))
            surface.blit(overlay, (0, 0))
        if self.distortion > 0.35:
            self._draw_distortion(surface)

    def _draw_channel(self, surface: pygame.Surface, rect: pygame.Rect, channel: Channel) -> None:
        colour = channel.colour
        ui.draw_panel(surface, rect, border=colour if channel.in_zone else ui.RED, alpha=190)
        ui.draw_text(surface, channel.label, (rect.x + 16, rect.y + 12), 22, colour, bold=True)
        status = "LOCKED" if channel.locked > 0 else ("IN SYNC" if channel.in_zone else "OUT OF SYNC")
        ui.draw_text(surface, status, (rect.right - 16, rect.y + 12), 20,
                     ui.LIME if channel.in_zone else ui.RED, align="topright", bold=True,
                     glow=0.0 if channel.in_zone else ui.pulse(self.time, 10))

        wave_rect = pygame.Rect(rect.x + 16, rect.y + 44, rect.width - 32, rect.height - 92)
        pygame.draw.rect(surface, (8, 10, 24), wave_rect, border_radius=6)

        # Ghost target waveform, then the live player waveform on top.
        self._draw_wave(surface, wave_rect, channel.target, tuple(c // 3 for c in colour), 0.0, 2)
        self._draw_wave(surface, wave_rect, channel.value, colour, channel.phase, 3)

        # Tuning strip: target zone + current knob position.
        strip = pygame.Rect(rect.x + 16, rect.bottom - 40, rect.width - 32, 22)
        pygame.draw.rect(surface, (18, 20, 40), strip, border_radius=6)
        zone_x = strip.x + (channel.target - channel.zone) * strip.width
        zone_w = max(6.0, channel.zone * 2 * strip.width)
        zone_rect = pygame.Rect(int(zone_x), strip.y, int(zone_w), strip.height)
        pygame.draw.rect(surface, (*ui.LIME, 90) if channel.in_zone else (70, 30, 40),
                         zone_rect.clip(strip), border_radius=6)
        pygame.draw.rect(surface, ui.LIME if channel.in_zone else ui.RED, zone_rect.clip(strip), 2, border_radius=6)
        marker_x = strip.x + clamp(channel.value, 0.0, 1.0) * strip.width
        pygame.draw.polygon(surface, ui.WHITE, [
            (marker_x, strip.y - 8), (marker_x - 8, strip.y - 22), (marker_x + 8, strip.y - 22)])
        pygame.draw.line(surface, ui.WHITE, (marker_x, strip.y), (marker_x, strip.bottom), 3)
        if channel.locked > 0:
            ui.draw_text(surface, f"LOCK {channel.locked:.1f}s", (strip.centerx, strip.centery), 16,
                         ui.BG, align="center", bold=True)

    def _draw_wave(self, surface, rect: pygame.Rect, value: float, colour, phase: float, width: int) -> None:
        points = []
        frequency = 1.2 + value * 9.0
        amplitude = rect.height * 0.42
        steps = max(24, rect.width // 4)
        for i in range(steps + 1):
            t = i / steps
            x = rect.x + t * rect.width
            y = rect.centery + math.sin(t * frequency * math.tau + phase) * amplitude
            points.append((x, y))
        if len(points) > 1:
            pygame.draw.lines(surface, colour, False, points, width)

    def _draw_core(self, surface: pygame.Surface, shake) -> None:
        width, height = surface.get_size()
        centre = (int(width * 0.83 + shake[0]), int(height * 0.42 + shake[1]))
        radius = int(min(width, height) * 0.11)
        instability = 1.0 - clamp(self.stability / STABILITY_MAX, 0.0, 1.0)
        colour = ui.lerp_color(ui.LIME, ui.RED, instability)
        pulse = 1.0 + 0.09 * math.sin(self.time * (4.0 + 10.0 * instability))
        ui.draw_glow_circle(surface, centre, radius * 0.7 * pulse, colour, layers=3)
        pygame.draw.circle(surface, ui.BG, centre, radius)
        pygame.draw.circle(surface, colour, centre, radius, 3)
        for i in range(8):
            angle = self.time * (0.6 + instability * 3) + i * math.tau / 8
            r = radius * (0.35 + 0.5 * abs(math.sin(self.time * 2 + i)))
            pygame.draw.circle(surface, colour,
                               (int(centre[0] + math.cos(angle) * r), int(centre[1] + math.sin(angle) * r)),
                               max(2, int(radius * 0.09)))
        ui.draw_text(surface, "CORE", (centre[0], centre[1] + radius + 18), 18, ui.TEXT_DIM, align="center")

        # Warning lamps
        for i, (label, active, colour_on) in enumerate((
            ("HEAT", self.heat > 0.65, ui.RED),
            ("CHARGE", self.charge > 0.65, ui.AMBER),
            ("SYNC", not all(c.in_zone for c in self.channels), ui.MAGENTA),
        )):
            x = int(width * 0.83 - 84 + i * 84)
            y = int(height * 0.72)
            lit = active and self.alarm_light > 0.5
            pygame.draw.circle(surface, colour_on if lit else (34, 34, 54), (x, y), 15)
            pygame.draw.circle(surface, colour_on if active else (60, 60, 84), (x, y), 15, 2)
            ui.draw_text(surface, label, (x, y + 22), 14, ui.TEXT_DIM, align="center")

    def _draw_distortion(self, surface: pygame.Surface) -> None:
        """Cheap CRT tear: shift a few scanline bands sideways."""
        width, height = surface.get_size()
        bands = int(2 + self.distortion * 5)
        for _ in range(bands):
            y = random.randint(0, max(1, height - 12))
            band_h = random.randint(4, 14)
            shift = int(random.uniform(-14, 14) * self.distortion)
            try:
                strip = surface.subsurface((0, y, width, min(band_h, height - y))).copy()
            except ValueError:
                continue
            surface.blit(strip, (shift, y))

    def _draw_gauges(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        heat_rect = pygame.Rect(int(width * 0.06), int(height * 0.87), int(width * 0.28), 20)
        ui.draw_text(surface, "HEAT  [B2 VENT]", (heat_rect.x, heat_rect.y - 8), 16, ui.TEXT_DIM, align="bottomleft")
        ui.draw_bar(surface, heat_rect, clamp(self.heat, 0, 1), ui.lerp_color(ui.LIME, ui.RED, clamp(self.heat, 0, 1)))
        charge_rect = pygame.Rect(int(width * 0.38), int(height * 0.87), int(width * 0.28), 20)
        ui.draw_text(surface, "CORE CHARGE  [B4 DISCHARGE]", (charge_rect.x, charge_rect.y - 8), 16,
                     ui.TEXT_DIM, align="bottomleft")
        ui.draw_bar(surface, charge_rect, clamp(self.charge, 0, 1), ui.AMBER)

    def draw_hud(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        self.draw_default_hud(surface)
        stability = clamp(self.stability / STABILITY_MAX, 0.0, 1.0)
        ui.draw_text(surface, "STABILITY", (width // 2, 18), 18, ui.TEXT_DIM, align="midtop")
        bar = pygame.Rect(width // 2 - 180, 40, 360, 20)
        ui.draw_bar(surface, bar, stability, ui.lerp_color(ui.RED, ui.LIME, stability), segments=10)
        ui.draw_text(surface, f"T+{self.survived:6.1f}s", (width - 24, 52), 20, ui.TEXT_DIM,
                     align="topright")
        if self.combo > 1:
            ui.draw_text(surface, f"COMBO x{self.combo}", (width - 24, 78), 22, ui.LIME,
                         align="topright", bold=True)

        for i, event in enumerate(self.events):
            ui.draw_text(surface, f"{event.name} {event.time_left:.0f}s", (24, 58 + i * 24), 18,
                         event.colour, bold=True)

        if self.alarm is not None:
            self._draw_alarm(surface)

    def _draw_alarm(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        alarm = self.alarm
        t = alarm.time_left / max(alarm.duration, 1e-4)
        rect = pygame.Rect(0, 0, int(width * 0.46), 84)
        rect.center = (width // 2, int(height * 0.155))
        blink = ui.pulse(self.time, 14.0)
        ui.draw_panel(surface, rect, color=(46, 10, 18), border=alarm.colour, alpha=int(180 + 60 * blink))
        ui.draw_text(surface, alarm.label, (rect.centerx, rect.centery - 12), 32, alarm.colour,
                     align="center", bold=True, glow=blink)
        ui.draw_text(surface, f"BUTTON {alarm.button}", (rect.centerx, rect.centery + 20), 20, ui.TEXT,
                     align="center", bold=True)
        timer = pygame.Rect(rect.x + 14, rect.bottom - 12, rect.width - 28, 6)
        ui.draw_bar(surface, timer, t, ui.RED if t < 0.4 else ui.AMBER, radius=3)

    def result_lines(self):
        return [
            (f"SURVIVED {self.survived:.1f}s", ui.CYAN),
            (f"BEST ALARM COMBO x{self.best_combo}", ui.LIME),
        ]
