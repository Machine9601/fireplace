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


# --- LEG_RLK_082
def test_deathbringer_saurfang():
    game = dk_game()
    saurfang = game.player1.give("LEG_RLK_082").play()
    assert saurfang.taunt and (saurfang.atk, saurfang.health) == (4, 6)
    assert Race.UNDEAD in saurfang.races
    game.player1.give(FIREBALL).play(target=saurfang)
    # Returned to the hand, costing Health instead of Mana
    assert saurfang.zone == Zone.HAND
    back = game.player1.hand[-1]
    assert back is saurfang
    assert back.card_costs_health
    assert back.cost == 5
    game.player1.used_mana = 10
    health = game.player1.hero.health
    back.play()
    assert game.player1.hero.health == health - 5
    assert game.player1.used_mana == 10
    assert back.zone == Zone.PLAY


def test_deathbringer_saurfang_needs_the_health():
    game = dk_game()
    saurfang = game.player1.give("LEG_RLK_082").play()
    game.player1.give(FIREBALL).play(target=saurfang)
    back = game.player1.hand[-1]
    game.player1.used_mana = 0
    game.player1.hero.set_current_health(5)
    # 5 Health for a 5 cost: the hero would die
    assert not back.is_playable()
    game.player1.hero.set_current_health(6)
    assert back.is_playable()


def test_deathbringer_saurfang_comes_back_again():
    game = dk_game()
    saurfang = game.player1.give("LEG_RLK_082").play()
    game.player1.give(FIREBALL).play(target=saurfang)
    back = game.player1.hand[-1]
    back.play()
    assert back.zone == Zone.PLAY
    game.player1.used_mana = 0
    game.player1.give(FIREBALL).play(target=back)
    # Every death brings it back, costing Health again
    assert back.zone == Zone.HAND and back.card_costs_health
    assert game.player1.hand[-1] is back


# --- RLK_720
def test_gnome_muncher():
    game = dk_game(class2=CardClass.MAGE)
    muncher = game.player1.give("RLK_720").play()
    assert muncher.taunt and muncher.lifesteal
    assert (muncher.atk, muncher.health) == (5, 6)
    wisp = game.player2.summon(WISP)
    crocolisk = game.player2.summon(CROCOLISK)
    golem = game.player2.summon(WAR_GOLEM)
    game.player1.hero.set_current_health(20)
    game.end_turn()
    # It attacked the lowest Health enemy, the Wisp, and healed by its Lifesteal
    assert wisp.zone == Zone.GRAVEYARD
    assert crocolisk.damage == 0 and golem.damage == 0
    assert muncher.damage == 1
    assert game.player1.hero.health == 25
    # A forced attack does not use the Muncher's own attack
    assert muncher.num_attacks == 0


def test_gnome_muncher_attacks_the_hero_when_alone():
    game = dk_game()
    game.player1.give("RLK_720").play()
    game.end_turn()
    assert game.player2.hero.health == 25


def test_gnome_muncher_attacks_the_lowest_health_character_even_the_hero():
    game = dk_game()
    game.player1.give("RLK_720").play()
    game.player2.hero.set_current_health(6)
    golem = game.player2.summon(WAR_GOLEM)
    game.end_turn()
    assert game.player2.hero.health == 1
    assert golem.damage == 0


def test_gnome_muncher_only_at_the_end_of_its_owners_turn():
    game = dk_game()
    game.player1.give("RLK_720").play()
    game.end_turn()
    assert game.player2.hero.health == 25
    wisp = game.player2.summon(WISP)
    # The other player's turn ends: the Muncher does not attack
    game.end_turn()
    assert wisp.zone == Zone.PLAY and game.player2.hero.health == 25


def test_gnome_muncher_takes_one_of_two_equal_targets():
    game = dk_game()
    game.player1.give("RLK_720").play()
    wisps = [game.player2.summon(WISP), game.player2.summon(WISP)]
    game.end_turn()
    assert sorted(w.zone for w in wisps) == [Zone.PLAY, Zone.GRAVEYARD]


def test_gnome_muncher_ignores_taunt():
    game = dk_game()
    game.player1.give("RLK_720").play()
    footman = game.player2.summon(GOLDSHIRE_FOOTMAN)  # 1/2 Taunt
    wisp = game.player2.summon(WISP)
    game.end_turn()
    assert wisp.zone == Zone.GRAVEYARD
    assert footman.damage == 0


# --- RLK_025
def test_frost_strike():
    game = dk_game()
    enemy = game.player2.summon(CROCOLISK)
    frost_strike = game.player1.give("RLK_025")
    assert game.player2.hero not in frost_strike.targets
    frost_strike.play(target=enemy)
    assert enemy.zone == Zone.GRAVEYARD
    choice = game.player1.choice
    assert choice and len(choice.cards) == 3
    for card in choice.cards:
        assert card.card_class == CardClass.DEATHKNIGHT, card
        assert card.cost_frost > 0, card
        assert sum(card.runes) < 3, card
    picked = choice.cards[1]
    choice.choose(picked)
    assert game.player1.hand[-1].id == picked.id


def test_frost_strike_that_does_not_kill_discovers_nothing():
    game = dk_game()
    golem = game.player2.summon(WAR_GOLEM)
    game.player1.give("RLK_025").play(target=golem)
    assert golem.damage == 3
    assert not game.player1.choice


def test_frost_strike_on_a_friendly_minion():
    game = dk_game()
    wisp = game.player1.summon(WISP)
    game.player1.give("RLK_025").play(target=wisp)
    assert wisp.zone == Zone.GRAVEYARD
    assert game.player1.choice


# --- RLK_511
def test_harbinger_of_winter():
    game = dk_game()
    icy_touch = game.player1.card("RLK_038", zone=Zone.DECK)  # a Frost spell
    fireball = game.player1.card(FIREBALL, zone=Zone.DECK)  # a Fire spell
    wisp = game.player1.card(WISP, zone=Zone.DECK)
    harbinger = game.player1.give("RLK_511").play()
    assert (harbinger.atk, harbinger.health) == (3, 2)
    assert not game.player1.hand
    game.player1.give(FIREBALL).play(target=harbinger)
    assert harbinger.zone == Zone.GRAVEYARD
    assert icy_touch.zone == Zone.HAND
    assert fireball.zone == Zone.DECK and wisp.zone == Zone.DECK


def test_harbinger_of_winter_draws_one_of_the_frost_spells():
    game = dk_game()
    spells = [game.player1.card("RLK_038", zone=Zone.DECK), game.player1.card("RLK_015", zone=Zone.DECK)]
    harbinger = game.player1.summon("RLK_511")
    game.player1.give(FIREBALL).play(target=harbinger)
    assert sorted(s.zone for s in spells) == [Zone.DECK, Zone.HAND]


def test_harbinger_of_winter_without_a_frost_spell():
    game = dk_game()
    fireball = game.player1.card(FIREBALL, zone=Zone.DECK)
    harbinger = game.player1.summon("RLK_511")
    game.player1.give(MOONFIRE).play(target=harbinger)
    game.player1.give(MOONFIRE).play(target=harbinger)
    assert harbinger.zone == Zone.GRAVEYARD
    assert fireball.zone == Zone.DECK
