"""Game state machines and headless play-throughs of all four games."""

import pygame
import pytest

from arcade.game import COUNTDOWN, GAME_OVER, INTRO, PAUSED, PLAYING
from arcade.simulated_controller import SimulatedController
from games import GAMES

DT = 1 / 60.0


def advance(app, seconds):
    for _ in range(int(seconds / DT)):
        app.step(DT, [])


def start(app, game_id):
    game = GAMES[game_id](app)
    app.set_scene(game, transition=False)
    assert game.state == INTRO
    game.start_countdown()
    assert game.state == COUNTDOWN
    advance(app, 3.2)
    assert game.state == PLAYING
    return game


@pytest.mark.parametrize("game_id", sorted(GAMES))
def test_game_runs_and_reaches_playing(app, game_id):
    controller = SimulatedController()
    app.replace_controller(controller)
    game = start(app, game_id)
    controller.sweep(1, 0.1, 0.9, 1.5).sweep(2, 0.9, 0.2, 1.5).tap(1).tap(2).tap(3).tap(4)
    advance(app, 6.0)
    assert game.state in (PLAYING, GAME_OVER)
    assert game.score >= 0


@pytest.mark.parametrize("game_id", sorted(GAMES))
def test_pause_resume_restart_and_quit(app, game_id):
    controller = SimulatedController()
    app.replace_controller(controller)
    game = start(app, game_id)

    game.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    assert game.state == PAUSED
    game.pause_index = 0
    game._activate_pause_item()
    assert game.state == PLAYING

    game.set_state(PAUSED)
    game.pause_index = 1                      # RESTART
    game._activate_pause_item()
    assert game.state == COUNTDOWN

    game.set_state(PAUSED)
    game.pause_index = 2                      # QUIT TO ARCADE
    game._activate_pause_item()
    app.step(DT, [])
    assert app.scene is not game


@pytest.mark.parametrize("game_id", sorted(GAMES))
def test_game_over_then_restart(app, game_id):
    controller = SimulatedController()
    app.replace_controller(controller)
    game = start(app, game_id)
    game.score = 4321
    game.game_over("TEST")
    assert game.state == GAME_OVER
    advance(app, 1.0)
    game.start_countdown()
    assert game.state == COUNTDOWN
    assert game.score in (0, 0.0)


@pytest.mark.parametrize("game_id", sorted(GAMES))
def test_high_score_persistence(app, game_id):
    game = GAMES[game_id](app)
    if not game.tracks_high_score:
        pytest.skip(f"{game_id} is a versus game and does not track a score")
    app.set_scene(game, transition=False)
    game.score = 9999
    game.game_over("TEST")
    assert game.new_high_score
    assert app.settings.high_score(game.game_id) == 9999


@pytest.mark.parametrize("game_id", sorted(GAMES))
def test_controller_loss_pauses_the_game(app, game_id):
    game = start(app, game_id)
    game.on_controller_lost()
    assert game.state == PAUSED


@pytest.mark.parametrize("size", [(1024, 600), (1280, 720), (1920, 1080)])
def test_games_render_at_several_window_sizes(app, size):
    surface = pygame.Surface(size)
    for game_id in sorted(GAMES):
        game = GAMES[game_id](app)
        app.set_scene(game, transition=False)
        game.on_resize(size)
        game.start_countdown()
        game.set_state("playing")
        for _ in range(30):
            game.update(DT, app.controller)
            game.draw(surface)


def test_neon_drift_crashes_end_the_run(app):
    from games.neon_drift import MAX_DAMAGE, NeonDrift, RoadObject
    from arcade import ui

    game = NeonDrift(app)
    app.set_scene(game, transition=False)
    game.start_countdown()
    game.set_state(PLAYING)
    for _ in range(MAX_DAMAGE):
        game.invulnerable = 0.0
        game._crash(RoadObject(0.0, 0.0, "traffic", ui.CYAN))
    assert game.state == GAME_OVER
    assert game.damage == MAX_DAMAGE


def test_twin_pong_scores_and_wins(app):
    from games.twin_pong import WIN_SCORE, TwinPong

    game = TwinPong(app)
    app.set_scene(game, transition=False)
    game.start_countdown()
    game.set_state(PLAYING)
    game.player1.score = WIN_SCORE
    game.update(DT, app.controller)
    assert game.state == GAME_OVER
    assert game.winner == 1


def test_twin_pong_shield_saves_the_ball(app):
    from games.twin_pong import Ball, TwinPong

    game = TwinPong(app)
    app.set_scene(game, transition=False)
    game.player1.shield = 5.0
    ball = Ball(-50, 300, -400, 0)
    assert game._concede(game.player1, game.player2, ball) is True
    assert game.player2.score == 0
    assert ball.vx > 0


def test_reactor_sync_wrong_button_penalises(app):
    from games.reactor_sync import Alarm, ReactorSync
    from arcade import ui

    game = ReactorSync(app)
    app.set_scene(game, transition=False)
    game.start_countdown()
    game.set_state(PLAYING)
    game.alarm = Alarm(2, "VENT COOLANT!", ui.LIME, 2.0, 2.0)
    before = game.stability
    assert game._answer_alarm(1) is True
    assert game.stability < before

    game.alarm = Alarm(2, "VENT COOLANT!", ui.LIME, 2.0, 2.0)
    score_before = game.score
    assert game._answer_alarm(2) is True
    assert game.score > score_before
    assert game.alarm is None


def test_orbital_defender_shield_absorbs_damage(app):
    from games.orbital_defender import OrbitalDefender

    game = OrbitalDefender(app)
    app.set_scene(game, transition=False)
    game.start_countdown()
    game.set_state(PLAYING)
    game.shield_up = True
    hull = game.hp
    game._damage_station(20, game.centre)
    assert game.hp == hull
    assert game.shield < 100.0
