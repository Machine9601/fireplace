"""The League of Explorers, Blackrock Mountain and Naxxramas encounters as the
official game plays them (Hearthstone WP-121): the hero powers that were
missing, the escapes, the bosses in several phases."""

import pytest
from utils import *
from utils import _empty_mulligan

from fireplace import enums
from fireplace.exceptions import GameOver, InvalidAction


class RealManaGame(CoinRules, BaseGame):
    """A game whose players start at 0 Mana Crystals, as in a real game."""


def _boss_game(hero1, hero2="HERO_01", deck=None, deck2=None, game_class=BaseTestGame):
    """A game where player1 (the first to play) is the boss `hero1`."""
    deck = deck if deck is not None else [WISP] * 20
    deck2 = deck2 if deck2 is not None else [WISP] * 20
    player1 = Player("Player1", list(deck), hero1)
    player2 = Player("Player2", list(deck2), hero2)
    game = game_class(players=(player1, player2))
    game.start()
    _empty_mulligan(game)
    if game.player1 is not player1:
        game.end_turn()
    return game, player1, player2


def db_passive(id):
    return fireplace.cards.db[id].tags.get(enums.PASSIVE_HERO_POWER)


def _turn(game):
    """End the turn of the current player, then the other's: back to him."""
    game.end_turn()
    game.end_turn()


def test_scarvash_swaps_his_hero_power():
    # Chieftain Scarvash: "Passive Hero Power: Enemy minions cost (2) more.
    # Swap at the start of your turn." (Trogg Hate Minions! / Trogg Hate
    # Spells!, heroic: "cost (11)").
    for hero, more in (("LOEA05_01", None), ("LOEA05_01h", 11)):
        player1 = Player("Player1", [WISP] * 20, hero)
        player2 = Player("Player2", [WISP] * 20, "HERO_08")
        game = BaseTestGame(players=(player1, player2))
        game.start()
        _empty_mulligan(game)
        boss, other = player1, player2
        assert db_passive(boss.hero.power.id)
        if game.current_player is not boss:
            # Before his first turn: minions cost more, spells do not.
            assert boss.hero.power.id in ("LOEA05_02", "LOEA05_02h")
            wisp = other.give(WISP)
            fireball = other.give("CS2_029")
            assert wisp.cost == (more if more else 2)
            assert fireball.cost == 4
            game.end_turn()
        wisp = other.give(WISP)
        fireball = other.give("CS2_029")
        # Start of his turn: spells cost more, minions do not.
        assert boss.hero.power.id in ("LOEA05_03", "LOEA05_03h")
        assert wisp.cost == 0
        assert fireball.cost == (more if more else 6)
        game.end_turn()
        assert fireball.cost == (more if more else 6)
        game.end_turn()
        # And back: minions.
        assert boss.hero.power.id in ("LOEA05_02a", "LOEA05_02ha")
        assert wisp.cost == (more if more else 2)
        assert fireball.cost == 4
        with pytest.raises(InvalidAction):
            boss.hero.power.use()


def test_lady_nazjar_pearl_of_the_tides():
    # Lady Naz'jar: "At the end of your turn, replace all minions with new ones
    # that cost (1) more."; heroic: "replace all minions with new ones. Yours
    # cost (1) more."
    for hero, enemy_more in (("LOEA12_1", 1), ("LOEA12_1H", 0)):
        game, boss, other = _boss_game(hero)
        assert db_passive(boss.hero.power.id)
        with pytest.raises(InvalidAction):
            boss.hero.power.use()
        mine = boss.summon("CS2_182")  # Chillwind Yeti, 4
        theirs = other.summon(WISP)  # Wisp, 0
        game.end_turn()
        assert len(boss.field) == 1 and len(other.field) == 1
        assert boss.field[0] is not mine and boss.field[0].cost == 5
        assert other.field[0] is not theirs and other.field[0].cost == enemy_more
        # Only at the end of her own turn.
        kept = boss.field[0]
        game.end_turn()
        assert boss.field[0] is kept


def test_majordomo_then_ragnaros():
    # Ragnaros the Firelord (boss): "Defeating the flamewaker causes him to
    # summon forth Ragnaros the Firelord, and the second stage of the battle
    # begins." (8 Health and DIE, INSECT!; heroic 30 and DIE, INSECTS!)
    for hero, ragnaros, health, power in (
        ("BRMA06_1", "BRMA06_3", 8, "BRM_027p"),
        ("BRMA06_1H", "BRMA06_3H", 30, "BRM_027pH"),
    ):
        game, boss, other = _boss_game(hero)
        game.end_turn()
        boss.hero.set_current_health(3)
        other.give("CS2_029").play(target=boss.hero)  # Fireball: 6 damage
        assert game.state != State.COMPLETE
        assert boss.playstate == PlayState.PLAYING
        assert boss.hero.id == ragnaros
        assert boss.hero.health == health and boss.hero.damage == 0
        assert boss.hero.power.id == power
        # Ragnaros falls: the boss is defeated.
        boss.hero.set_current_health(2)
        with pytest.raises(GameOver):
            other.give("CS2_029").play(target=boss.hero)
        assert other.playstate == PlayState.WON


def test_nefarian_onyxia_nefarian():
    # Nefarian (Hidden Laboratory): his Armor gone, Onyxia comes (15 Health,
    # Onyxiclaw, Nefarian Strikes! 1, 2, 1, 3, 1, 4, 0 then 20 fireballs);
    # she falls, Nefarian returns with the Health he had and clears the board.
    game, boss, other = _boss_game("BRMA17_2")
    boss.hero.armor = 10
    game.end_turn()
    wisp = other.summon(WISP)
    other.give("CS2_029").play(target=boss.hero)  # 6 into the Armor
    assert boss.hero.id == "BRMA17_2" and boss.hero.armor == 4
    other.give("CS2_029").play(target=boss.hero)  # 4 Armor, then 2 damage
    assert boss.hero.id == "BRMA17_3"
    assert boss.hero.health == 15
    assert boss.hero.power.id == "BRMA17_8" and db_passive("BRMA17_8")
    assert boss.weapon.id == "BRMA17_9"
    health = other.hero.health
    game.end_turn()
    assert other.hero.health == health - 1
    game.end_turn()
    boss.hero.set_current_health(1)
    other.give("CS2_029").play(target=boss.hero)
    assert boss.playstate == PlayState.PLAYING
    assert boss.hero.id == "BRMA17_2"
    assert boss.hero.health == 28
    assert boss.hero.power.id == "BRMA17_5"
    assert wisp.dead and len(other.field) == 0
    game.end_turn()
    # No more Onyxia strikes.
    health = other.hero.health
    game.end_turn()
    assert other.hero.health == health


def test_nefarian_killed_at_once_skips_the_stages():
    game, boss, other = _boss_game("BRMA17_2H")
    boss.hero.armor = 30
    boss.hero.set_current_health(1)
    game.end_turn()
    with pytest.raises(GameOver):
        game.cheat_action(other.hero, [Hit(boss.hero, 31)])
    assert other.playstate == PlayState.WON
    assert boss.hero.id == "BRMA17_2H"


def _choose(player, id):
    choice = player.choice
    assert choice is not None
    card = next(c for c in choice.cards if c.id == id)
    choice.choose(card)


def test_temple_escape():
    # Temple Escape: the boss is Immune, has no deck, and the player wins when
    # the "turns to escape" count (10, down at the end of the boss's turn)
    # reaches 0; each boss's turn brings its obstacles, some a path to choose
    # at the start of the player's turn (the wiki's "Event order").
    game, boss, other = _boss_game("LOEA04_01", deck=[], deck2=[WISP] * 30)
    power = boss.hero.power
    assert power.id == "LOEA04_02" and db_passive("LOEA04_02")
    with pytest.raises(InvalidAction):
        power.use()
    # Boss's turn 1: a Zombie Chow; the player then chooses at the pool.
    assert [m.id for m in boss.field] == ["FP1_001"]
    game.end_turn()
    assert power.data_num_1 == 9
    assert sorted(c.id for c in other.choice.cards) == ["LOEA04_28a", "LOEA04_28b"]
    # The draw of the turn waits for the choice (as Pick Your Fate's does).
    hand = len(other.hand)
    _choose(other, "LOEA04_28a")  # Drink Deeply: draw a card
    assert len(other.hand) == hand + 2
    assert not other.hand.filter(id="LOEA04_28a")
    # The boss is Immune.
    other.give("CS2_029").play(target=boss.hero)
    assert boss.hero.damage == 0
    game.end_turn()
    # Turn 2: an Oasis Snapjaw, then the Pit of Spikes.
    assert boss.field.filter(id="CS2_119")
    game.end_turn()
    _choose(other, "LOEA04_06b")  # Walk Across Gingerly: take 5 damage
    assert other.hero.damage == 5
    game.end_turn()
    # Turn 3: an Orsis Guard, and a Rolling Boulder on the player's side.
    assert boss.field.filter(id="LOEA04_13bt")
    assert other.field[-1].id == "LOE_024t"
    game.end_turn()
    assert other.choice is None
    game.end_turn()
    # Turn 4: the Eye; touching it heals and awakens the statue.
    game.end_turn()
    _choose(other, "LOEA04_29a")
    assert other.hero.damage == 0
    assert boss.field.filter(id="LOEA04_27")
    game.end_turn()
    # Turn 5: every minion is destroyed.
    assert len(boss.field) == 0 and len(other.field) == 0
    game.end_turn()
    game.end_turn()
    # Turn 6: an Anubisath Temple Guard.
    assert [m.id for m in boss.field] == ["LOEA04_24"]
    game.end_turn()
    game.end_turn()
    # Turn 7: an Obsidian Destroyer, then the Darkness: the Shortcut.
    assert boss.field.filter(id="LOE_009")
    game.end_turn()
    assert power.data_num_1 == 3
    _choose(other, "LOEA04_30a")
    assert power.data_num_1 == 2
    assert boss.field.filter(id="CS2_186")
    game.end_turn()
    # The Seething Statue is skipped: turn 9, the Giant Insects.
    assert not boss.field.filter(id="LOEA04_25")
    assert len(boss.field.filter(id="LOEA04_23")) == 2
    game.end_turn()
    assert power.data_num_1 == 1
    assert game.state != State.COMPLETE
    game.end_turn()
    with pytest.raises(GameOver):
        game.end_turn()
    # The count reaches 0 at the end of the boss's turn: the player escaped.
    assert game.state == State.COMPLETE
    assert other.playstate == PlayState.WON
    assert boss.playstate == PlayState.LOST


def test_temple_escape_heroic():
    game, boss, other = _boss_game("LOEA04_01h", deck=[], deck2=[WISP] * 30)
    assert boss.hero.power.id == "LOEA04_02h"
    assert [m.id for m in boss.field] == ["CS2_200"]
    for _ in range(2):
        game.end_turn()
        if other.choice:
            _choose(other, other.choice.cards[1].id)
        game.end_turn()
    assert len(boss.field.filter(id="LOEA04_13bth")) == 2


def test_mine_cart_rush():
    # Mine Cart Rush: the boss is Immune and summons 3 minions the first
    # time, then 2 each turn; the Mine Cart is locked at two Mana Crystals;
    # Barrel Forward gets the player 1 turn closer to the Exit.
    game, boss, other = _boss_game(
        "LOEA07_02", "LOEA07_01", deck=[], deck2=["LOEA07_25"] * 30, game_class=RealManaGame
    )
    power = boss.hero.power
    assert power.id == "LOEA07_03" and db_passive("LOEA07_03")
    troggs = ("LOEA07_09", "LOEA07_11", "LOEA07_12", "LOEA07_14")
    assert len(boss.field) == 3 and all(m.id in troggs for m in boss.field)
    game.end_turn()
    assert other.max_mana == 2 and other.mana == 2
    other.give("LOEA07_21").play()
    assert power.data_num_1 == 8
    game.end_turn()
    assert len(boss.field) == 5
    game.end_turn()
    assert other.max_mana == 2
    assert boss.hero.damage == 0 and boss.hero.immune
    ends = 0
    while game.state != State.COMPLETE:
        ends += 1
        try:
            game.end_turn()
        except GameOver:
            break
    # 10 turns to escape, less the Barrel Forward: 7 more turns of the boss,
    # each after one of the player.
    assert power.data_num_1 == 0
    assert ends == 14
    assert other.playstate == PlayState.WON
