"""One Night in Karazhan as the official game plays it (Hearthstone WP-123):
the hero powers, the boss cards and the rules of each encounter, the chess
board excepted (WP-123b). What counts: the card's text, then
hearthstone.wiki.gg."""

import pytest
from utils import *
from utils import _empty_mulligan

from fireplace import enums
from fireplace.exceptions import GameOver, InvalidAction


class RealManaGame(CoinRules, BaseGame):
    """A game whose players start at 0 Mana Crystals, as in a real game."""


def _boss_game(hero1, hero2="HERO_08", deck=None, deck2=None, game_class=BaseTestGame):
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


##
# The prologue: An Uninvited Guest (Prince Malchezaar against Medivh)


def test_legion_summons_an_abyssal():
    # Legion: "Hero Power Summon a 6/6 Abyssal."
    for hero in ("KARA_00_01", "KARA_00_01H"):
        game, boss, other = _boss_game(hero)
        assert boss.hero.power.id in ("KARA_00_02", "KARA_00_02H")
        assert not db_passive(boss.hero.power.id)
        boss.hero.power.use()
        assert len(boss.field) == 1 and boss.field[0].id == "KARA_00_02a"
        assert boss.field[0].atk == 6 and boss.field[0].health == 6


def test_malchezaar_starts_with_five_mana_crystals():
    # An Uninvited Guest, Notes: "Prince Malchezaar starts with 5 Mana
    # Crystals." His opponent starts as usual.
    for hero in ("KARA_00_01", "KARA_00_01H"):
        player1 = Player("Player1", [WISP] * 20, hero)
        player2 = Player("Player2", [WISP] * 20, "KARA_00_03")
        game = RealManaGame(players=(player1, player2))
        game.start()
        _empty_mulligan(game)
        boss, other = player1, player2
        if game.current_player is boss:
            assert boss.max_mana == 6
            game.end_turn()
            assert other.max_mana == 1
        else:
            assert other.max_mana == 1
            game.end_turn()
            assert boss.max_mana == 6


def test_brilliance_draws_three():
    # Brilliance (Medivh): "Hero Power Draw 3 cards."
    for hero in ("KARA_00_03", "KARA_00_03H"):
        game, player, other = _boss_game(hero)
        hand = len(player.hand)
        player.hero.power.use()
        assert len(player.hand) == hand + 3


def test_archmages_insight():
    # "Your spells cost (0) this turn."
    game, player, other = _boss_game("KARA_00_03")
    fireball = player.give(FIREBALL)
    wisp = player.give(WISP)
    player.give("KARA_00_05").play()
    assert fireball.cost == 0
    player.give(PYROBLAST)
    assert player.hand[-1].cost == 0
    assert wisp.cost == 0 and player.give("CS2_182").cost == 4
    game.end_turn()
    game.end_turn()
    assert fireball.cost == 4


def test_arcane_power():
    # "You have Spell Damage +5 this turn."
    game, player, other = _boss_game("KARA_00_03")
    player.give("KARA_00_06").play()
    assert player.spellpower == 5
    player.give(MOONFIRE).play(target=other.hero)
    assert other.hero.health == 30 - 6
    game.end_turn()
    assert player.spellpower == 0


def test_astral_portal():
    # "Summon a random Legendary minion."
    game, player, other = _boss_game("KARA_00_03")
    player.give("KARA_00_07").play()
    assert len(player.field) == 1
    assert player.field[0].rarity == Rarity.LEGENDARY


def test_archmages_apprentice():
    # "Whenever you cast a spell, shuffle a copy of it into your deck."
    game, player, other = _boss_game("KARA_00_03")
    player.give("KARA_00_08").play()
    deck = len(player.deck)
    player.give(MOONFIRE).play(target=other.hero)
    assert len(player.deck) == deck + 1
    assert player.deck.filter(id=MOONFIRE)
    # Not the enemy's spells.
    game.end_turn()
    other.give(MOONFIRE).play(target=player.hero)
    assert len(player.deck) == deck + 1


def test_mage_armor():
    # "Gain 10 Armor."
    game, player, other = _boss_game("KARA_00_03")
    player.give("KARA_00_09").play()
    assert player.hero.armor == 10


def test_mysterious_rune():
    # "Put 5 random Mage Secrets into the battlefield."
    game, player, other = _boss_game("KARA_00_03")
    player.give("KARA_00_10").play()
    assert len(player.secrets) == 5
    assert len({s.id for s in player.secrets}) == 5
    for secret in player.secrets:
        assert secret.card_class == CardClass.MAGE


def test_guardians_evocation():
    # "Gain 5 Mana Crystals this turn only."
    player1 = Player("Player1", [WISP] * 20, "KARA_00_03")
    player2 = Player("Player2", [WISP] * 20, "HERO_08")
    game = RealManaGame(players=(player1, player2))
    game.start()
    _empty_mulligan(game)
    player = game.current_player
    player.give("KARA_00_11").play()
    assert player.mana == 1 + 5
    game.end_turn()
    game.end_turn()
    assert player.mana == 2
