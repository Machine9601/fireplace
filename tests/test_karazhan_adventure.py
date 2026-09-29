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


##
# The Parlor: Silverware Golem, Magic Mirror

PLATE = "KAR_A02_01"


def _plates(player):
    return player.field.filter(id=PLATE)


def test_be_our_guest():
    # "Hero Power Summon a 1/1 Plate." (heroic: "two 1/1 Plates")
    for hero, count in (("KAR_A02_12", 1), ("KAR_A02_12H", 2)):
        game, boss, other = _boss_game(hero)
        assert not db_passive(boss.hero.power.id)
        boss.hero.power.use()
        assert len(_plates(boss)) == count
        assert _plates(boss)[0].atk == 1 and _plates(boss)[0].health == 1


def test_silverware_auras():
    # Cup: "Plates have +1 Attack." (heroic +3) ; Fork: "Plates have
    # Charge." ; Knife: "Plates have Taunt."
    for cup, more in (("KAR_A02_05", 1), ("KAR_A02_05H", 3)):
        game, boss, other = _boss_game("KAR_A02_12")
        plate = boss.summon(PLATE)
        wisp = boss.summon(WISP)
        boss.summon(cup)
        assert plate.atk == 1 + more and wisp.atk == 1
        enemy_plate = other.summon(PLATE)
        assert enemy_plate.atk == 1
    for fork in ("KAR_A02_03", "KAR_A02_03H"):
        game, boss, other = _boss_game("KAR_A02_12")
        boss.summon(fork)
        plate = boss.summon(PLATE)
        assert plate.charge and plate.can_attack()
        assert not boss.field[0].charge
    for knife in ("KAR_A02_04", "KAR_A02_04H"):
        game, boss, other = _boss_game("KAR_A02_12")
        boss.summon(knife)
        plate = boss.summon(PLATE)
        assert plate.taunt and not boss.field[0].taunt


def test_pitcher():
    # Pitcher (heroic): "Battlecry: Give a minion +3/+3."
    game, boss, other = _boss_game("KAR_A02_12H")
    wisp = boss.summon(WISP)
    boss.give("KAR_A02_06H").play(target=wisp)
    assert wisp.atk == 4 and wisp.health == 4


def test_set_the_table_pour_a_round_tossing_plates():
    # Tossing Plates: "Summon five 1/1 Plates." ; Set the Table: "Give your
    # Plates +1/+1." (heroic +2/+2) ; Pour a Round: "Draw a card for each of
    # your Plates."
    game, boss, other = _boss_game("KAR_A02_12")
    boss.give("KAR_A02_11").play()
    assert len(_plates(boss)) == 5
    boss.give("KAR_A02_09").play()
    assert all(p.atk == 2 and p.health == 2 for p in _plates(boss))
    game.end_turn()
    game.end_turn()
    boss.give("KAR_A02_09H").play()
    assert all(p.atk == 4 and p.health == 4 for p in _plates(boss))
    hand = len(boss.hand)
    boss.give("KAR_A02_10").play()
    assert len(boss.hand) == hand + 5


def test_reflections_normal_copies_for_whoever_plays():
    # Magic Mirror: "Passive Hero Power Whenever a minion is played, summon a
    # 1/1 copy of it." In normal, each player gets the copy of the minion he
    # plays; in heroic, "Magic Mirror summons a 1/1 copy of it".
    game, boss, other = _boss_game("KAR_A01_01")
    assert db_passive("KAR_A01_02")
    with pytest.raises(InvalidAction):
        boss.hero.power.use()
    boss.give("CS2_182").play()
    assert len(boss.field) == 2
    copy = boss.field[1]
    assert copy.id == "CS2_182" and copy.atk == 1 and copy.health == 1
    game.end_turn()
    other.give("CS2_182").play()
    assert len(other.field) == 2 and len(boss.field) == 2
    assert other.field[1].atk == 1 and other.field[1].health == 1
    # A summoned minion is not played.
    other.summon(WISP)
    assert len(other.field) == 3 and len(boss.field) == 2


def test_reflections_heroic_copies_for_the_mirror():
    game, boss, other = _boss_game("KAR_A01_01H")
    assert db_passive("KAR_A01_02H")
    game.end_turn()
    other.give("CS2_182").play()
    assert len(other.field) == 1 and len(boss.field) == 1
    assert boss.field[0].id == "CS2_182" and boss.field[0].atk == 1
    game.end_turn()
    boss.give(WISP).play()
    assert len(boss.field) == 3
