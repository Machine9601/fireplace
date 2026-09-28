"""The death knight: its base hero and Hero Power, the Corpses, the runes and
the 26 cards of Path of Arthas (texts of HearthstoneJSON build 253216)."""

from utils import *

from fireplace import cards as cards_db


PATH_OF_ARTHAS = [
    "RLK_042", "RLK_038", "RLK_110", "RLK_516", "RLK_018", "RLK_056", "RLK_057",
    "RLK_066", "RLK_083", "RLK_711", "RLK_712", "RLK_015", "RLK_087", "RLK_512",
    "RLK_731", "RLK_062", "RLK_118", "RLK_713", "RLK_740", "RLK_745", "RLK_504",
    "RLK_730", "RLK_086", "RLK_505", "RLK_063", "RLK_122",
]


def dk_game(deck1=None, deck2=None, class2=CardClass.DEATHKNIGHT):
    """An empty-deck game: player1 is a death knight, player2 of `class2`.
    Not a Standard game: Path of Arthas is not in the fork's Standard sets
    (a Standard game draws nothing of it at random)."""
    player1 = Player(
        "Player1", deck1 or [], CardClass.DEATHKNIGHT.default_hero, is_standard=False
    )
    player1.cant_fatigue = True
    player2 = Player("Player2", deck2 or [], class2.default_hero, is_standard=False)
    player2.cant_fatigue = True
    game = BaseTestGame(players=(player1, player2))
    game.start()
    for player in game.players:
        if player.choice:
            player.choice.choose()
    return game


# --- the data -------------------------------------------------------------


def test_path_of_arthas_in_carddefs():
    db = cards_db.db
    collectible = [
        id for id, card in db.items()
        if card.card_set == CardSet.PATH_OF_ARTHAS and card.collectible
    ]
    assert sorted(collectible) == sorted(PATH_OF_ARTHAS)
    for id in PATH_OF_ARTHAS:
        assert db[id].card_class == CardClass.DEATHKNIGHT, id
        assert db[id].tags.get(GameTag.CARDTEXT) or db[id].description, id


def test_path_of_arthas_stats():
    # (cost, attack, health or durability), build 253216
    stats = {
        "RLK_042": (0, 0, 0), "RLK_038": (1, 0, 0), "RLK_110": (1, 1, 2),
        "RLK_516": (1, 2, 2), "RLK_018": (2, 0, 0), "RLK_056": (2, 0, 0),
        "RLK_057": (2, 0, 0), "RLK_066": (2, 2, 3), "RLK_083": (2, 2, 3),
        "RLK_711": (2, 3, 2), "RLK_712": (2, 0, 0), "RLK_015": (3, 0, 0),
        "RLK_087": (3, 0, 0), "RLK_512": (3, 0, 0), "RLK_731": (3, 2, 5),
        "RLK_062": (4, 1, 3), "RLK_118": (4, 0, 0), "RLK_713": (4, 4, 3),
        "RLK_740": (4, 4, 2), "RLK_745": (4, 2, 4), "RLK_504": (5, 4, 4),
        "RLK_730": (5, 0, 0), "RLK_086": (6, 4, 3), "RLK_505": (6, 5, 5),
        "RLK_063": (7, 0, 0), "RLK_122": (9, 0, 0),
    }
    db = cards_db.db
    for id, (cost, atk, health) in stats.items():
        card = db[id]
        if card.type == CardType.WEAPON:
            # A weapon of a recent CardDefs.xml gives its durability as
            # HEALTH: the fork reads DURABILITY (patch 21.8)
            assert (card.cost, card.atk, card.durability) == (cost, atk, health), id
        else:
            assert (card.cost, card.atk, card.health) == (cost, atk, health), id


def test_death_knight_hero_and_hero_power():
    db = cards_db.db
    assert CardClass.DEATHKNIGHT.default_hero == "HERO_11"
    hero = db["HERO_11"]
    assert hero.type == CardType.HERO
    assert hero.card_class == CardClass.DEATHKNIGHT
    assert hero.health == 30
    assert hero.hero_power == "HERO_11bp"
    assert db["HERO_11bp"].name == "Ghoul Charge"
    assert db["HERO_11bp"].cost == 2
    assert db["HERO_11bpt"].name == "Frail Ghoul"
    assert db["HERO_11bpt"].races == [Race.UNDEAD]


def test_rune_tags():
    db = cards_db.db
    runes = lambda id: tuple(
        db[id].tags.get(tag, 0)
        for tag in (GameTag.COST_BLOOD, GameTag.COST_FROST, GameTag.COST_UNHOLY)
    )
    assert runes("RLK_730") == (2, 0, 0)  # Blood Boil
    assert runes("RLK_063") == (0, 3, 0)  # Frostwyrm's Fury
    assert runes("RLK_118") == (0, 0, 2)  # Tomb Guardians
    assert runes("RLK_087") == (0, 0, 0)  # Asphyxiate
    assert runes("RLK_042") == (0, 2, 0)  # Horn of Winter


# --- the runes ------------------------------------------------------------


def test_runes_of_a_card():
    game = dk_game()
    blood_boil = game.player1.give("RLK_730")
    assert blood_boil.runes == (2, 0, 0)
    assert blood_boil.runes.blood == 2
    assert game.player1.give("RLK_063").runes == (0, 3, 0)
    assert game.player1.give("RLK_118").runes == (0, 0, 2)
    assert game.player1.give("RLK_087").runes == (0, 0, 0)
    # Any other card has no rune
    assert game.player1.give(FIREBALL).runes == (0, 0, 0)
    assert game.player1.give(WISP).runes.frost == 0


# --- the Corpses ----------------------------------------------------------


def test_corpse_when_a_friendly_minion_dies():
    game = dk_game(class2=CardClass.MAGE)
    assert game.player1.corpses == 0
    wisp = game.player1.give(WISP).play()
    enemy_wisp = game.player2.summon(WISP)
    game.player1.give(MOONFIRE).play(target=wisp)
    assert game.player1.corpses == 1
    # Every class tracks its Corpses (patch 25.4.0)
    game.player1.give(MOONFIRE).play(target=enemy_wisp)
    assert game.player1.corpses == 1
    assert game.player2.corpses == 1


def test_no_corpse_for_a_hero_or_a_weapon():
    game = dk_game()
    game.player1.give(LIGHTS_JUSTICE).play()
    game.player1.give("RLK_516").play()  # Bone Breaker destroys the first weapon
    assert game.player1.corpses == 0


def test_corpse_before_the_deathrattle():
    from fireplace.actions import Deathrattle

    seen = []
    do = Deathrattle.do

    def spy(self, source, target):
        seen.append(target.controller.corpses)
        return do(self, source, target)

    game = dk_game()
    gnome = game.player1.give("EX1_029").play()  # Leper Gnome
    Deathrattle.do = spy
    try:
        game.player1.give(MOONFIRE).play(target=gnome)
    finally:
        Deathrattle.do = do
    assert seen == [1]


def test_corpses_survive_a_deep_copy():
    import copy

    game = dk_game()
    game.player1.give(MOONFIRE).play(target=game.player1.give(WISP).play())
    other = copy.deepcopy(game)
    assert other.player1.corpses == 1
    other.player1.corpses = 5
    assert game.player1.corpses == 1


def test_spend_corpses():
    from fireplace.actions import SpendCorpses

    game = dk_game()
    player = game.player1
    hero = player.hero
    player.corpses = 3
    armor = GainArmor(FRIENDLY_HERO, SpendCorpses.AMOUNT)
    # Not enough: nothing is spent, nothing happens
    game.queue_actions(hero, [SpendCorpses(CONTROLLER, 4).then(armor)])
    assert player.corpses == 3 and hero.armor == 0
    game.queue_actions(hero, [SpendCorpses(CONTROLLER, 2).then(armor)])
    assert player.corpses == 1 and hero.armor == 2
    assert player.corpses_spent_this_game == 2
    # Up to: as many as the player has
    game.queue_actions(hero, [SpendCorpses(CONTROLLER, 5, up_to=True).then(armor)])
    assert player.corpses == 0 and hero.armor == 3
    game.queue_actions(hero, [SpendCorpses(CONTROLLER, 5, up_to=True).then(armor)])
    assert player.corpses == 0 and hero.armor == 3
    assert player.corpses_spent_this_game == 3


# --- the hero and its Hero Power ------------------------------------------


def test_ghoul_charge():
    game = dk_game()
    assert game.player1.hero.id == "HERO_11"
    assert game.player1.hero.power.id == "HERO_11bp"
    game.player1.hero.power.use()
    ghoul = game.player1.field[0]
    assert ghoul.id == "HERO_11bpt"
    assert ghoul.atk == 1 and ghoul.health == 1
    assert ghoul.charge and ghoul.can_attack()
    assert Race.UNDEAD in ghoul.races
    game.end_turn()
    assert ghoul.zone == Zone.GRAVEYARD
    assert not game.player1.field
    assert game.player1.corpses == 1


def test_frail_ghoul_dies_only_at_the_end_of_its_owners_turn():
    game = dk_game()
    game.end_turn()
    ghoul = game.player1.summon("HERO_11bpt")
    game.end_turn()
    assert ghoul.zone == Zone.PLAY
    game.end_turn()
    assert ghoul.zone == Zone.GRAVEYARD


def test_ghoul_frenzy_by_justicar_trueheart():
    game = dk_game()
    game.player1.give("AT_132").play()
    assert game.player1.hero.power.id == "HERO_11bp2"
    game.player1.hero.power.use()
    ghoul = game.player1.field[-1]
    assert ghoul.id == "HERO_11bp2t"
    assert ghoul.atk == 2 and ghoul.health == 1 and ghoul.charge
    game.end_turn()
    assert ghoul.zone == Zone.GRAVEYARD


# --- the cards --------------------------------------------------------------

CROCOLISK = "CS2_120"  # 2/3
WAR_GOLEM = "CS2_186"  # 7/7


# --- RLK_042
def test_horn_of_winter():
    game = dk_game()
    game.player1.used_mana = 5
    game.player1.give("RLK_042").play()
    assert game.player1.used_mana == 3
    assert game.player1.mana == 7
    game.player1.give("RLK_042").play()
    game.player1.give("RLK_042").play()
    assert game.player1.used_mana == 0


