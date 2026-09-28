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
    """An empty-deck game: player1 is a death knight, player2 of `class2`."""
    player1 = Player("Player1", deck1 or [], CardClass.DEATHKNIGHT.default_hero)
    player1.cant_fatigue = True
    player2 = Player("Player2", deck2 or [], class2.default_hero)
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
