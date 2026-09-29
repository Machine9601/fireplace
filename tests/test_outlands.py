from utils import *


def test_kaelthas_sunstrider():
    game = prepare_empty_game()
    fireball = game.player1.give(FIREBALL)
    game.player1.give(THE_COIN).play()
    game.player1.give(THE_COIN).play()
    assert fireball.cost == 4
    game.player1.give("BT_255").play()
    assert fireball.cost == 0
    game.player1.give(THE_COIN).play()
    assert fireball.cost == 4
    game.player1.give(THE_COIN).play()
    assert fireball.cost == 4
    game.player1.give(THE_COIN).play()
    assert fireball.cost == 0


def test_metamorphosis():
    game = prepare_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    game.player1.hero_power.use()
    old_hero_power = game.player1.hero_power
    game.player1.give("BT_429").play()
    assert game.player1.hero_power == "BT_429p"
    game.player1.hero_power.use(target=game.player2.hero)
    assert game.player1.hero_power == "BT_429p2"
    assert game.player1.hero_power.exhausted
    game.skip_turn()
    game.player1.hero_power.use(target=game.player2.hero)
    assert game.player1.hero_power == old_hero_power
    assert not game.player1.hero_power.exhausted


def test_imprisoned_antaen():
    game = prepare_game()
    antaen = game.player1.give("BT_934").play()
    assert antaen.dormant
    assert antaen.dormant_turns == 2
    game.skip_turn()
    assert antaen.dormant
    assert antaen.dormant_turns == 1
    game.skip_turn()
    assert not antaen.dormant
    assert antaen.dormant_turns == 0
    assert game.player2.hero.health == 20
    game.end_turn()
    sap = game.player2.give("EX1_581")
    sap.play(target=antaen)
    game.end_turn()
    antaen.play()
    assert antaen.dormant
    assert antaen.dormant_turns == 2
    game.skip_turn()
    assert antaen.dormant
    assert antaen.dormant_turns == 1
    game.skip_turn()
    assert not antaen.dormant
    assert antaen.dormant_turns == 0
    assert game.player2.hero.health == 10


def test_darkglare():
    game = prepare_game()
    game.player1.give("BT_307").play()
    assert game.player1.mana == 7
    game.player1.give(FIREBALL).play(target=game.player1.hero)
    assert game.player1.mana == 7 - 4 + 2


def test_maiev_shadowsong():
    game = prepare_game()
    wisp = game.player1.give(WISP).play()
    assert not wisp.dormant
    assert wisp.dormant_turns == 0
    game.player1.give("BT_737").play(target=wisp)
    assert wisp.dormant
    assert wisp.dormant_turns == 2
    game.skip_turn()
    assert wisp.dormant
    assert wisp.dormant_turns == 1
    game.skip_turn()
    assert not wisp.dormant
    assert wisp.dormant_turns == 0


def test_eye_beam():
    # Lifesteal. Deal 3 damage to a minion: it needs its target, and only a minion (WP-146)
    game = prepare_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    golem = game.player2.summon("CS2_186")
    game.player1.hero.set_current_health(20)
    eye_beam = game.player1.give("BT_801")
    assert eye_beam.requires_target()
    assert golem in eye_beam.targets
    assert game.player2.hero not in eye_beam.targets
    assert game.player1.hero not in eye_beam.targets
    eye_beam.play(target=golem)
    assert golem.damage == 3
    assert game.player1.hero.health == 20 + 3


def test_eye_beam_from_the_middle_of_the_hand():
    # Not an outcast play: the `play` script does the damage, at full cost
    game = prepare_empty_game()
    golem = game.player2.summon("CS2_186")
    game.player1.give(WISP)
    eye_beam = game.player1.give("BT_801")
    game.player1.give(WISP)
    assert not eye_beam.play_outcast
    assert eye_beam.cost == 3
    eye_beam.play(target=golem)
    assert golem.damage == 3
    assert game.player1.mana == 10 - 3
