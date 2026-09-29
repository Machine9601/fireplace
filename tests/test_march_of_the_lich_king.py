"""The 20 death knight cards of March of the Lich King that the three decks of
Visions of Sayge (Blood, Frost, Unholy) ask for: texts of HearthstoneJSON
build 253216. They are reserved for that Brawl: never collectible here."""

from test_path_of_arthas import dk_game
from utils import *

from fireplace import cards as cards_db
from fireplace.utils import random_class

SAYGE = [
    "RLK_503", "RLK_958", "RLK_708", "LEG_RLK_082", "RLK_720", "RLK_025",
    "RLK_511", "LEG_RLK_710", "RLK_709", "RLK_223", "LEG_RLK_224",
    "LEG_RLK_039", "RLK_061", "LEG_RLK_705", "RLK_707", "LEG_RLK_085",
    "LEG_RLK_744", "RLK_048", "RLK_060", "LEG_RLK_071",
]

# Their tokens and enchantments (build 253216)
TOKENS = [
    "RLK_039t",  # Grain Crate
    "RLK_070t",  # Undead Peasant
    "RLK_061t",  # Risen Footman
    "RLK_008t",  # Risen Ghoul
    "RLK_085t",  # Risen Golem
    "RLK_705t",  # Shambling Zombie
]
ENCHANTMENTS = [
    "RLK_085e", "RLK_707e", "RLK_707e2", "RLK_710e", "RLK_958e", "RLK_048e",
]


# --- the data ---------------------------------------------------------------


def test_the_twenty_cards_are_in_carddefs():
    db = cards_db.db
    # (cost, attack, health or durability, runes blood/frost/unholy), build 253216
    stats = {
        "RLK_503": (1, 1, 3, (0, 0, 0)), "RLK_958": (1, 1, 2, (0, 0, 0)),
        "RLK_708": (3, 2, 2, (0, 0, 0)), "LEG_RLK_082": (5, 4, 6, (2, 0, 0)),
        "RLK_720": (6, 5, 6, (0, 0, 0)), "RLK_025": (2, 0, 0, (0, 1, 0)),
        "RLK_511": (2, 3, 2, (0, 1, 0)), "LEG_RLK_710": (3, 2, 3, (0, 2, 0)),
        "RLK_709": (4, 0, 0, (0, 1, 0)), "RLK_223": (4, 3, 3, (0, 1, 0)),
        "LEG_RLK_224": (6, 3, 6, (0, 2, 0)), "LEG_RLK_039": (1, 0, 0, (0, 0, 2)),
        "RLK_061": (2, 2, 2, (0, 0, 2)), "LEG_RLK_705": (3, 0, 0, (0, 0, 1)),
        "RLK_707": (4, 0, 0, (0, 0, 3)), "LEG_RLK_085": (8, 9, 7, (0, 0, 3)),
        "LEG_RLK_744": (9, 8, 8, (0, 0, 1)), "RLK_048": (3, 0, 0, (0, 0, 1)),
        "RLK_060": (5, 0, 0, (0, 0, 1)), "LEG_RLK_071": (7, 4, 6, (1, 0, 0)),
    }
    assert sorted(stats) == sorted(SAYGE)
    for id, (cost, atk, health, runes) in stats.items():
        card = db[id]
        assert card.card_class == CardClass.DEATHKNIGHT, id
        assert card.tags.get(GameTag.CARDTEXT) or card.description, id
        assert (card.cost, card.atk) == (cost, atk), id
        if card.type == CardType.WEAPON:
            assert card.durability == health, id
        else:
            assert card.health == health, id
        assert tuple(
            card.tags.get(tag, 0)
            for tag in (GameTag.COST_BLOOD, GameTag.COST_FROST, GameTag.COST_UNHOLY)
        ) == runes, id
    types = {
        "RLK_503": CardType.MINION, "LEG_RLK_710": CardType.WEAPON,
        "RLK_025": CardType.SPELL, "LEG_RLK_071": CardType.MINION,
    }
    for id, type in types.items():
        assert db[id].type == type, id


def test_their_tokens_and_enchantments_are_in_carddefs():
    db = cards_db.db
    for id in TOKENS:
        assert db[id].type in (CardType.MINION, CardType.SPELL), id
    for id in ENCHANTMENTS:
        assert db[id].type == CardType.ENCHANTMENT, id
    assert (db["RLK_061t"].atk, db["RLK_061t"].health) == (1, 3)
    assert (db["RLK_008t"].atk, db["RLK_008t"].health) == (2, 2)
    assert (db["RLK_085t"].atk, db["RLK_085t"].health) == (1, 1)
    assert (db["RLK_705t"].atk, db["RLK_705t"].health) == (1, 1)
    assert (db["RLK_070t"].atk, db["RLK_070t"].health) == (2, 2)
    assert db["RLK_039t"].type == CardType.SPELL


def test_the_twenty_cards_are_reserved_for_visions_of_sayge():
    """Not collectible: no random deck, no random class, no Standard pool and
    no Discover ever offers them (a deck that names them plays them)."""
    db = cards_db.db
    for id in SAYGE:
        assert not db[id].collectible, id
    reserved = set(SAYGE)
    for card_class in (CardClass.MAGE, CardClass.WARRIOR, CardClass.DEATHKNIGHT):
        assert not reserved & set(random_draft(card_class))
    game = prepare_empty_game()
    source = game.player1.hero
    assert game.is_standard
    for picker in (RandomMinion(), RandomCollectible(), RandomSpell(), RandomWeapon()):
        pool = picker.find_cards(source)
        assert pool and not reserved & set(pool)
    # The same in a game that is not Standard (all the sets)
    game = dk_game()
    source = game.player1.hero
    assert not game.is_standard
    for picker in (RandomMinion(), RandomCollectible(), RandomSpell(), RandomWeapon()):
        pool = picker.find_cards(source)
        assert pool and not reserved & set(pool)
    # A deck that names them plays them
    game.player1.give("RLK_503").play()
    assert game.player1.field[0].id == "RLK_503"


# --- the cards ----------------------------------------------------------------

CROCOLISK = "CS2_120"  # 2/3
WAR_GOLEM = "CS2_186"  # 7/7
BRANN = "LOE_077"  # Brann Bronzebeard


# --- RLK_503
def test_body_bagger():
    game = dk_game()
    bagger = game.player1.give("RLK_503").play()
    assert (bagger.atk, bagger.health) == (1, 3)
    assert Race.UNDEAD in bagger.races
    assert game.player1.corpses == 1
    assert game.player2.corpses == 0
    game.player1.give("RLK_503").play()
    assert game.player1.corpses == 2


def test_body_bagger_with_brann():
    game = dk_game()
    game.player1.give(BRANN).play()
    game.player1.give("RLK_503").play()
    assert game.player1.corpses == 2


def test_gain_corpses_is_not_spending():
    game = dk_game()
    game.player1.give("RLK_503").play()
    assert game.player1.corpses_spent_this_game == 0


# --- RLK_958
def test_skeletal_sidekick():
    game = dk_game()
    undead = game.player1.summon("RLK_503")  # Body Bagger, an Undead
    wisp = game.player1.summon(WISP)
    enemy_undead = game.player2.summon("RLK_503")
    sidekick = game.player1.give("RLK_958")
    assert (sidekick.atk, sidekick.health) == (1, 2)
    assert Race.UNDEAD in sidekick.races
    assert sidekick.requires_target()
    # Friendly Undead only: not the Wisp, not the enemy's, not a hero
    assert sidekick.targets == [undead]
    sidekick.play(target=undead)
    assert undead.atk == 3 and undead.health == 3
    assert wisp.atk == 1
    assert enemy_undead.atk == 1


def test_skeletal_sidekick_without_a_target():
    game = dk_game()
    game.player1.summon(WISP)
    sidekick = game.player1.give("RLK_958")
    assert not sidekick.requires_target()
    sidekick.play()
    assert game.player1.field[-1] is sidekick
    assert sidekick.atk == 1


# --- RLK_708
def test_chillfallen_baron():
    game = dk_game()
    for _ in range(4):
        game.player1.card(WISP, zone=Zone.DECK)
    baron = game.player1.give("RLK_708")
    # (Its second tribe, Draenei, is a tag of a newer build that the reader of
    # CardDefs.xml does not know: nothing here reacts to it.)
    assert Race.UNDEAD in baron.races
    hand = len(game.player1.hand)  # with the Baron
    baron.play()
    # The Baron leaves the hand, the Battlecry draws a card
    assert len(game.player1.hand) == hand
    assert len(game.player1.deck) == 3
    # The Deathrattle draws another
    game.player1.give(FIREBALL).play(target=baron)
    assert baron.zone == Zone.GRAVEYARD
    assert len(game.player1.hand) == hand + 1
    assert len(game.player1.deck) == 2
