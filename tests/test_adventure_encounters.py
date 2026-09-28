"""The League of Explorers, Blackrock Mountain and Naxxramas encounters as the
official game plays them (Hearthstone WP-121): the hero powers that were
missing, the escapes, the bosses in several phases."""

import pytest
from utils import *
from utils import _empty_mulligan

from fireplace import enums
from fireplace.exceptions import InvalidAction


def _boss_game(hero1, hero2="HERO_01", deck=None, deck2=None):
    """A game where player1 (the first to play) is the boss `hero1`."""
    deck = deck if deck is not None else [WISP] * 20
    deck2 = deck2 if deck2 is not None else [WISP] * 20
    player1 = Player("Player1", list(deck), hero1)
    player2 = Player("Player2", list(deck2), hero2)
    game = BaseTestGame(players=(player1, player2))
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
