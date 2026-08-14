"""TWIN PONG - two players, one breadboard.

Player 1: POT 1 paddle, B1 ability (blast), B2 serve / secondary.
Player 2: POT 2 paddle, B3 ability (blast), B4 serve / secondary.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import List, Tuple

import pygame

from arcade import ui
from arcade.game import BaseGame, approach, clamp

WIN_SCORE = 7
BASE_SPEED = 430.0
MAX_SPEED = 1150.0
SERVE_DELAY = 1.6
PADDLE_H_RATIO = 0.19
PADDLE_W = 16
BLAST_COOLDOWN = 4.5
BLAST_TIME = 0.35

POWERUP_TYPES = (
    ("MULTI BALL", ui.CYAN),
    ("GIANT PADDLE", ui.LIME),
    ("SHRINK RIVAL", ui.MAGENTA),
    ("SLOW MOTION", ui.VIOLET),
    ("SPEED BALL", ui.AMBER),
    ("CURVE BALL", ui.CYAN),
    ("SHIELD", ui.LIME),
    ("REVERSE RIVAL", ui.RED),
)


@dataclass
class Ball:
    x: float
    y: float
    vx: float
    vy: float
    radius: float = 11.0
    spin: float = 0.0
    trail: List[Tuple[float, float]] = field(default_factory=list)
    owner: int = 0          # who touched it last (1 or 2), 0 = nobody


@dataclass
class Player:
    index: int
    colour: Tuple[int, int, int]
    y: float = 0.5
    score: int = 0
    height_scale: float = 1.0
    blast: float = 0.0
    cooldown: float = 0.0
    shield: float = 0.0
    reversed_until: float = 0.0
    effect_label: str = ""
    effect_timer: float = 0.0
    glow: float = 0.0


@dataclass
class Pickup:
    x: float
    y: float
    vy: float
    name: str
    colour: Tuple[int, int, int]
    radius: float = 18.0
    spin: float = 0.0


class TwinPong(BaseGame):
    game_id = "twin_pong"
    title = "TWIN PONG"
    subtitle = "PLAYER 1  vs  PLAYER 2"
    accent = ui.LIME
    tracks_high_score = False
    control_hints = (
        ("P1  POT 1", "LEFT PADDLE"),
        ("P1  BUTTON 1", "BLAST"),
        ("P1  BUTTON 2", "SERVE"),
        ("P2  POT 2", "RIGHT PADDLE"),
        ("P2  BUTTON 3", "BLAST"),
        ("P2  BUTTON 4", "SERVE"),
    )

    def __init__(self, app):
        super().__init__(app)
        self.reset_game()

    # -------------------------------------------------------------- state

    def reset_game(self) -> None:
        self.player1 = Player(1, ui.CYAN)
        self.player2 = Player(2, ui.MAGENTA)
        self.balls: List[Ball] = []
        self.pickups: List[Pickup] = []
        self.serve_timer = SERVE_DELAY
        self.serving = random.choice((1, 2))
        self.rally = 0
        self.best_rally = 0
        self.slow_motion = 0.0
        self.pickup_timer = 6.0
        self.score = 0
        self.winner = 0
        self.round_flash = 0.0
        self.announce = ""
        self.announce_timer = 0.0

    @property
    def players(self):
        return (self.player1, self.player2)

    def paddle_rect(self, player: Player) -> pygame.Rect:
        width, height = self.size
        paddle_h = height * PADDLE_H_RATIO * player.height_scale
        x = width * 0.045 if player.index == 1 else width * 0.955 - PADDLE_W
        y = player.y * (height - paddle_h)
        return pygame.Rect(int(x), int(y), PADDLE_W, int(paddle_h))

    # ----------------------------------------------------------- gameplay

    def update_play(self, dt: float, controller) -> None:
        if self.slow_motion > 0.0:
            self.slow_motion -= dt
            dt_ball = dt * 0.45
        else:
            dt_ball = dt
        self.round_flash = max(0.0, self.round_flash - dt * 2.0)
        self.announce_timer = max(0.0, self.announce_timer - dt)

        self._update_players(dt, controller)

        if not self.balls:
            self.serve_timer -= dt
            quick = controller.button_pressed(2 if self.serving == 1 else 4)
            if self.serve_timer <= 0.0 or quick:
                self._serve(quick)
        self._update_balls(dt_ball)
        self._update_pickups(dt)

        for player in self.players:
            if player.score >= WIN_SCORE:
                self.winner = player.index
                self.game_over(f"PLAYER {player.index} WINS")

    def _update_players(self, dt: float, controller) -> None:
        for player in self.players:
            pot = controller.pot(player.index)
            if player.reversed_until > self.time:
                pot = 1.0 - pot
            player.y = approach(player.y, clamp(pot, 0.0, 1.0), 26.0, dt)
            player.cooldown = max(0.0, player.cooldown - dt)
            player.blast = max(0.0, player.blast - dt)
            player.shield = max(0.0, player.shield - dt)
            player.glow = max(0.0, player.glow - dt * 3.0)
            player.effect_timer = max(0.0, player.effect_timer - dt)
            if player.effect_timer <= 0.0:
                player.effect_label = ""
                player.height_scale = approach(player.height_scale, 1.0, 3.0, dt)

        if controller.button_pressed(1):
            self._blast(self.player1)
        if controller.button_pressed(3):
            self._blast(self.player2)

    def _blast(self, player: Player) -> None:
        """Short-range shove: knocks nearby balls away, hard."""
        if player.cooldown > 0.0:
            self.app.audio.play("fail", 0.35)
            return
        player.cooldown = BLAST_COOLDOWN
        player.blast = BLAST_TIME
        player.glow = 1.0
        rect = self.paddle_rect(player)
        self.app.audio.play("boost", 0.6)
        self.particles.burst(rect.center, 20, player.colour, speed=320, life=0.4,
                             direction=0.0 if player.index == 1 else math.pi, spread=2.2)
        reach = self.size[0] * 0.22
        for ball in self.balls:
            if abs(ball.x - rect.centerx) < reach:
                direction = 1.0 if player.index == 1 else -1.0
                speed = min(MAX_SPEED, math.hypot(ball.vx, ball.vy) * 1.45)
                angle = math.atan2(ball.y - rect.centery, abs(ball.x - rect.centerx) + 40) * 0.8
                ball.vx = direction * speed * math.cos(angle)
                ball.vy = speed * math.sin(angle)
                ball.owner = player.index
                self.shake.add(6.0)
                self.floaters.add("BLAST!", (ball.x, ball.y), player.colour, 26, 0.6)

    def _serve(self, quick: bool) -> None:
        width, height = self.size
        direction = 1.0 if self.serving == 1 else -1.0
        angle = random.uniform(-0.35, 0.35)
        speed = BASE_SPEED * (1.15 if quick else 1.0)
        self.balls.append(Ball(width * 0.5, height * 0.5,
                               math.cos(angle) * speed * direction, math.sin(angle) * speed))
        self.serve_timer = SERVE_DELAY
        self.rally = 0
        self.app.audio.play("serve")

    def _update_balls(self, dt: float) -> None:
        width, height = self.size
        remaining = []
        for position, ball in enumerate(self.balls):
            ball.vy += ball.spin * dt * 260.0
            ball.x += ball.vx * dt
            ball.y += ball.vy * dt
            ball.trail.append((ball.x, ball.y))
            if len(ball.trail) > 14:
                del ball.trail[0]

            if ball.y - ball.radius < 0 and ball.vy < 0:
                ball.y = ball.radius
                ball.vy *= -1
                self._wall_hit(ball)
            elif ball.y + ball.radius > height and ball.vy > 0:
                ball.y = height - ball.radius
                ball.vy *= -1
                self._wall_hit(ball)

            for player in self.players:
                if self._paddle_hit(ball, player):
                    break

            if ball.x < -40 or ball.x > width + 40:
                others = len(remaining) + len(self.balls) - position - 1
                if others > 0:
                    # Multi-ball: spare balls just leave the court quietly.
                    continue
                loser, scorer = ((self.player1, self.player2) if ball.x < -40
                                 else (self.player2, self.player1))
                if self._concede(loser, scorer, ball):
                    remaining.append(ball)   # shield save keeps it alive
                continue
            remaining.append(ball)
        self.balls = remaining

    def _wall_hit(self, ball: Ball) -> None:
        self.app.audio.play("bounce", 0.4)
        self.particles.burst((ball.x, ball.y), 6, ui.WHITE, speed=180, life=0.3, size=2)

    def _paddle_hit(self, ball: Ball, player: Player) -> bool:
        rect = self.paddle_rect(player)
        moving_towards = ball.vx < 0 if player.index == 1 else ball.vx > 0
        if not moving_towards:
            return False
        if not rect.inflate(ball.radius * 2, ball.radius * 2).collidepoint(ball.x, ball.y):
            return False
        offset = (ball.y - rect.centery) / max(1.0, rect.height / 2)
        offset = clamp(offset, -1.2, 1.2)
        speed = min(MAX_SPEED, math.hypot(ball.vx, ball.vy) * 1.07 + 18.0)
        angle = offset * 0.85
        direction = 1.0 if player.index == 1 else -1.0
        ball.vx = direction * speed * math.cos(angle)
        ball.vy = speed * math.sin(angle)
        ball.x = rect.right + ball.radius if player.index == 1 else rect.left - ball.radius
        ball.owner = player.index
        ball.spin = offset * 0.9 if ball.spin else 0.0
        player.glow = 1.0
        self.rally += 1
        self.best_rally = max(self.best_rally, self.rally)
        self.app.audio.play("bounce", 0.6 + min(0.4, self.rally * 0.03))
        self.particles.burst(rect.center, 12, player.colour, speed=260, life=0.35,
                             direction=0.0 if player.index == 1 else math.pi, spread=1.8)
        self.shake.add(2.0 + min(6.0, self.rally * 0.25))
        if self.rally and self.rally % 5 == 0:
            self.floaters.add(f"RALLY x{self.rally}!", (self.size[0] * 0.5, self.size[1] * 0.22),
                              ui.AMBER, 32, 1.0)
            self.app.audio.play("combo", 0.7)
        return True

    def _concede(self, loser: Player, scorer: Player, ball: Ball) -> bool:
        """Award the point.  Returns True when a shield kept the ball alive."""
        if loser.shield > 0.0:
            loser.shield = 0.0
            loser.effect_label = ""
            ball.vx = abs(ball.vx) if loser.index == 1 else -abs(ball.vx)
            ball.x = clamp(ball.x, 30, self.size[0] - 30)
            self.app.audio.play("shield")
            self.floaters.add("SHIELD SAVE!", (ball.x, ball.y), ui.LIME, 28, 0.9)
            return True
        scorer.score += 1
        self.serving = loser.index
        self.serve_timer = SERVE_DELAY
        self.round_flash = 1.0
        self.rally = 0
        self.app.audio.play("score")
        self.shake.add(10.0)
        self.particles.burst((ball.x, self.size[1] * 0.5), 30, scorer.colour, speed=380, life=0.7)
        self._announce(f"POINT PLAYER {scorer.index}", scorer.colour)
        # Losing a rally clears the loser's debuffs so comebacks stay possible.
        loser.height_scale = 1.0
        loser.effect_label = ""
        loser.reversed_until = 0.0
        return False

    def _announce(self, text: str, colour) -> None:
        self.announce = text
        self.announce_timer = 1.6
        self.floaters.add(text, (self.size[0] * 0.5, self.size[1] * 0.35), colour, 40, 1.2)

    # ------------------------------------------------------------ pickups

    def _update_pickups(self, dt: float) -> None:
        width, height = self.size
        self.pickup_timer -= dt
        if self.pickup_timer <= 0.0 and self.balls and len(self.pickups) < 3:
            self.pickup_timer = random.uniform(7.0, 12.0)
            name, colour = random.choice(POWERUP_TYPES)
            self.pickups.append(Pickup(width * random.uniform(0.35, 0.65),
                                       height * random.uniform(0.15, 0.85),
                                       random.uniform(-30, 30), name, colour))
        remaining = []
        for pickup in self.pickups:
            pickup.y += pickup.vy * dt
            pickup.spin += dt * 2.0
            if pickup.y < 40 or pickup.y > height - 40:
                pickup.vy *= -1
            hit = False
            for ball in self.balls:
                if math.hypot(ball.x - pickup.x, ball.y - pickup.y) < pickup.radius + ball.radius:
                    self._apply_powerup(pickup, ball)
                    hit = True
                    break
            if not hit:
                remaining.append(pickup)
        self.pickups = remaining

    def _apply_powerup(self, pickup: Pickup, ball: Ball) -> None:
        beneficiary = ball.owner or (1 if ball.vx > 0 else 2)
        player = self.player1 if beneficiary == 1 else self.player2
        rival = self.player2 if beneficiary == 1 else self.player1
        self.app.audio.play("powerup")
        self.particles.burst((pickup.x, pickup.y), 24, pickup.colour, speed=300, life=0.6)
        name = pickup.name
        if name == "MULTI BALL":
            for _ in range(2):
                angle = random.uniform(-0.6, 0.6)
                speed = math.hypot(ball.vx, ball.vy)
                sign = 1.0 if ball.vx > 0 else -1.0
                self.balls.append(Ball(ball.x, ball.y, sign * speed * math.cos(angle), speed * math.sin(angle),
                                       owner=ball.owner))
        elif name == "GIANT PADDLE":
            player.height_scale = 1.7
            player.effect_label, player.effect_timer = "GIANT", 9.0
        elif name == "SHRINK RIVAL":
            rival.height_scale = 0.6
            rival.effect_label, rival.effect_timer = "SHRUNK", 8.0
        elif name == "SLOW MOTION":
            self.slow_motion = 4.0
        elif name == "SPEED BALL":
            for b in self.balls:
                speed = min(MAX_SPEED, math.hypot(b.vx, b.vy) * 1.5)
                angle = math.atan2(b.vy, b.vx)
                b.vx, b.vy = math.cos(angle) * speed, math.sin(angle) * speed
        elif name == "CURVE BALL":
            ball.spin = random.choice((-1.0, 1.0)) * 1.2
        elif name == "SHIELD":
            player.shield = 12.0
            player.effect_label, player.effect_timer = "SHIELD", 12.0
        else:  # REVERSE RIVAL
            rival.reversed_until = self.time + 6.0
            rival.effect_label, rival.effect_timer = "REVERSED", 6.0
        self._announce(f"P{beneficiary}: {name}", pickup.colour)

    # -------------------------------------------------------------- render

    def draw_background(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        surface.fill(ui.BG)
        # Court halves tinted with each player's colour.
        for player, rect in ((self.player1, pygame.Rect(0, 0, width // 2, height)),
                             (self.player2, pygame.Rect(width // 2, 0, width // 2, height))):
            tint = pygame.Surface(rect.size, pygame.SRCALPHA)
            tint.fill((*player.colour, 14))
            surface.blit(tint, rect.topleft)
        for y in range(0, height, 34):
            pygame.draw.line(surface, (60, 64, 100), (width // 2, y), (width // 2, y + 18), 3)
        pygame.draw.circle(surface, (48, 52, 88), (width // 2, height // 2), int(height * 0.18), 2)
        # Top and bottom walls, so bounces read clearly.
        pygame.draw.line(surface, (70, 76, 120), (0, 1), (width, 1), 3)
        pygame.draw.line(surface, (70, 76, 120), (0, height - 2), (width, height - 2), 3)

    def draw_play(self, surface: pygame.Surface) -> None:
        shake = self.shake.offset
        for player in self.players:
            self._draw_paddle(surface, player, shake)
        for pickup in self.pickups:
            self._draw_pickup(surface, pickup, shake)
        for ball in self.balls:
            self._draw_ball(surface, ball, shake)
        if self.slow_motion > 0.0:
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((*ui.VIOLET, 30))
            surface.blit(overlay, (0, 0))
        if self.round_flash > 0.0:
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, int(50 * self.round_flash)))
            surface.blit(overlay, (0, 0))
        if not self.balls:
            self._draw_serve_prompt(surface)

    def _draw_paddle(self, surface, player: Player, shake) -> None:
        rect = self.paddle_rect(player).move(shake)
        colour = ui.WHITE if player.blast > 0 else player.colour
        glow = 6 + int(10 * player.glow)
        halo = pygame.Surface((rect.width + glow * 2, rect.height + glow * 2))
        pygame.draw.rect(halo, tuple(c // 5 for c in colour), halo.get_rect(), border_radius=10)
        surface.blit(halo, (rect.x - glow, rect.y - glow), special_flags=pygame.BLEND_ADD)
        pygame.draw.rect(surface, colour, rect, border_radius=6)
        pygame.draw.rect(surface, ui.WHITE, rect, 2, border_radius=6)
        if player.shield > 0:
            shield_rect = rect.inflate(26, 26)
            pygame.draw.rect(surface, ui.LIME, shield_rect, 3, border_radius=12)
        if player.blast > 0:
            reach = int(self.size[0] * 0.2)
            direction = 1 if player.index == 1 else -1
            wave = pygame.Rect(rect.centerx, rect.y - 20, reach * direction, rect.height + 40)
            wave.normalize()
            pygame.draw.rect(surface, colour, wave, 2, border_radius=8)

    def _draw_ball(self, surface, ball: Ball, shake) -> None:
        for i, (tx, ty) in enumerate(ball.trail):
            t = i / max(1, len(ball.trail))
            colour = tuple(int(c * t * 0.8) for c in (ui.WHITE if not ball.owner else
                                                      (ui.CYAN if ball.owner == 1 else ui.MAGENTA)))
            pygame.draw.circle(surface, colour, (int(tx + shake[0]), int(ty + shake[1])),
                               max(1, int(ball.radius * t * 0.8)))
        pos = (int(ball.x + shake[0]), int(ball.y + shake[1]))
        ui.draw_glow_circle(surface, pos, ball.radius, ui.WHITE, layers=2)

    def _draw_pickup(self, surface, pickup: Pickup, shake) -> None:
        pos = (int(pickup.x + shake[0]), int(pickup.y + shake[1]))
        points = []
        for i in range(6):
            angle = pickup.spin + i * math.tau / 6
            points.append((pos[0] + math.cos(angle) * pickup.radius, pos[1] + math.sin(angle) * pickup.radius))
        pygame.draw.polygon(surface, tuple(c // 3 for c in pickup.colour), points)
        pygame.draw.polygon(surface, pickup.colour, points, 2)
        ui.draw_text(surface, pickup.name.split()[0][:5], (pos[0], pos[1] + pickup.radius + 12), 14,
                     pickup.colour, align="center", bold=True)

    def _draw_serve_prompt(self, surface) -> None:
        width, height = surface.get_size()
        colour = ui.CYAN if self.serving == 1 else ui.MAGENTA
        button = "B2" if self.serving == 1 else "B4"
        ui.draw_text(surface, f"PLAYER {self.serving} SERVES", (width // 2, height * 0.42), 40, colour,
                     align="center", bold=True, glow=ui.pulse(self.time, 5))
        ui.draw_text(surface, f"press [{button}] to serve now  -  auto serve in {max(0.0, self.serve_timer):.1f}s",
                     (width // 2, height * 0.5), 22, ui.TEXT_DIM, align="center")

    # ----------------------------------------------------------------- HUD

    def draw_hud(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        ui.draw_text(surface, str(self.player1.score), (width * 0.32, 30), 76, ui.CYAN,
                     align="midtop", bold=True, glow=0.6)
        ui.draw_text(surface, str(self.player2.score), (width * 0.68, 30), 76, ui.MAGENTA,
                     align="midtop", bold=True, glow=0.6)
        ui.draw_text(surface, f"FIRST TO {WIN_SCORE}", (width // 2, 34), 20, ui.TEXT_DIM, align="midtop")
        # Labels sit inboard of the paddles so they never collide with them.
        ui.draw_text(surface, "PLAYER 1", (width * 0.18, 34), 22, ui.CYAN, align="midtop", bold=True)
        ui.draw_text(surface, "PLAYER 2", (width * 0.82, 34), 22, ui.MAGENTA, align="midtop", bold=True)

        for player, x in ((self.player1, width * 0.18), (self.player2, width * 0.82)):
            ready = player.cooldown <= 0.0
            label = "BLAST READY" if ready else f"BLAST {player.cooldown:.1f}s"
            ui.draw_text(surface, label, (x, 62), 17, ui.LIME if ready else ui.TEXT_DIM, align="midtop")
            if player.effect_label:
                ui.draw_text(surface, f"{player.effect_label} {player.effect_timer:.0f}s", (x, 84), 17,
                             ui.AMBER, align="midtop", bold=True)

        if self.rally >= 3:
            ui.draw_text(surface, f"RALLY {self.rally}", (width // 2, height - 40), 26, ui.AMBER,
                         align="center", bold=True, glow=ui.pulse(self.time, 8))
        if self.slow_motion > 0:
            ui.draw_text(surface, "SLOW MOTION", (width // 2, height - 70), 22, ui.VIOLET,
                         align="center", bold=True)

    def result_lines(self):
        return [
            (f"PLAYER 1  {self.player1.score}   -   {self.player2.score}  PLAYER 2", ui.TEXT),
            (f"LONGEST RALLY {self.best_rally}", ui.AMBER),
        ]

    def draw_game_over(self, surface: pygame.Surface) -> None:
        # Two-player game: show the winner instead of a single score/high score.
        super().draw_game_over(surface)
        width, height = surface.get_size()
        colour = ui.CYAN if self.winner == 1 else ui.MAGENTA
        ui.draw_text(surface, f"{self.player1.score} - {self.player2.score}", (width // 2, height * 0.42),
                     70, colour, align="center", bold=True, glow=1.0)
