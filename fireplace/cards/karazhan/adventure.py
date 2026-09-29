"""
One Night in Karazhan, the adventure (Hearthstone WP-123): the hero powers,
the boss cards and the rules of each encounter, as the official game plays
them. What counts: the card's text, then hearthstone.wiki.gg. The chess
board (Chess) is not here yet (WP-123b).
"""

from hearthstone.enums import Zone

from ...dsl.evaluator import Evaluator
from ...logging import log
from ..utils import *


##
# The prologue: An Uninvited Guest (Prince Malchezaar against Medivh)


class KARA_00_02:
    """Legion"""

    # "Hero Power Summon a 6/6 Abyssal." The wiki (An Uninvited Guest,
    # Notes): "Prince Malchezaar starts with 5 Mana Crystals." Legion is his
    # own, in this encounter only: the crystals come with it, when the game
    # starts (and his first turn gives one more, as for any player).
    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    activate = Summon(CONTROLLER, "KARA_00_02a")
    events = GameStart().on(GainMana(CONTROLLER, 5))


class KARA_00_02H:
    """Legion (Heroic)"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    activate = Summon(CONTROLLER, "KARA_00_02a")
    events = GameStart().on(GainMana(CONTROLLER, 5))


class KARA_00_04:
    """Brilliance"""

    activate = Draw(CONTROLLER) * 3


class KARA_00_04H:
    """Brilliance (Heroic)"""

    activate = Draw(CONTROLLER) * 3


class KARA_00_05:
    """Archmage's Insight"""

    # "Your spells cost (0) this turn."
    play = Buff(CONTROLLER, "KARA_00_05e")


class KARA_00_05e:
    update = Refresh(FRIENDLY_HAND + SPELL, {GameTag.COST: SET(0)})


class KARA_00_06:
    """Arcane Power"""

    # "You have Spell Damage +5 this turn."
    play = Buff(CONTROLLER, "KARA_00_06e")


class KARA_00_06e:
    # A player's Spell Damage is read from auras (Arcanotron does the same).
    update = Refresh(CONTROLLER, {GameTag.SPELLPOWER: +5})


class KARA_00_07:
    """Astral Portal"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    play = Summon(CONTROLLER, RandomLegendaryMinion())


class KARA_00_08:
    """Archmage's Apprentice"""

    events = OWN_SPELL_PLAY.on(Shuffle(CONTROLLER, Copy(Play.CARD)))


class KARA_00_09:
    """Mage Armor"""

    play = GainArmor(FRIENDLY_HERO, 10)


class KARA_00_10:
    """Mysterious Rune"""

    # "Put 5 random Mage Secrets into the battlefield." (five different
    # ones: a player cannot have the same Secret twice)
    play = (
        Summon(
            CONTROLLER,
            RandomSpell(
                secret=True, card_class=CardClass.MAGE, exclude=FRIENDLY_SECRETS
            ),
        )
        * 5
    )


class KARA_00_11:
    """Guardian's Evocation"""

    play = ManaThisTurn(CONTROLLER, 5)


##
# The Parlor: Silverware Golem

PLATES = FRIENDLY_MINIONS + ID("KAR_A02_01")


class KAR_A02_13:
    """Be Our Guest"""

    # The wiki: "Auto-cast" (A54: the boss's bot uses it when it sees fit).
    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    activate = Summon(CONTROLLER, "KAR_A02_01")


class KAR_A02_13H:
    """Be Our Guest (Heroic)"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    activate = Summon(CONTROLLER, "KAR_A02_01") * 2


class KAR_A02_03:
    """Fork"""

    update = Refresh(PLATES, buff="KAR_A02_03e")


class KAR_A02_03H:
    """Fork (Heroic)"""

    update = Refresh(PLATES, buff="KAR_A02_03e")


KAR_A02_03e = buff(charge=True)


class KAR_A02_04:
    """Knife"""

    update = Refresh(PLATES, buff="KAR_A02_04e")


class KAR_A02_04H:
    """Knife (Heroic)"""

    update = Refresh(PLATES, buff="KAR_A02_04e")


KAR_A02_04e = buff(taunt=True)


class KAR_A02_05:
    """Cup"""

    update = Refresh(PLATES, buff="KAR_A02_05e")


class KAR_A02_05H:
    """Cup (Heroic)"""

    update = Refresh(PLATES, buff="KAR_A02_05e2")


KAR_A02_05e = buff(atk=1)
KAR_A02_05e2 = buff(atk=3)


class KAR_A02_06H:
    """Pitcher (Heroic)"""

    requirements = {PlayReq.REQ_MINION_TARGET: 0, PlayReq.REQ_TARGET_IF_AVAILABLE: 0}
    play = Buff(TARGET, "KAR_A02_06He")


KAR_A02_06He = buff(+3, +3)


class KAR_A02_09:
    """Set the Table"""

    play = Buff(PLATES, "KAR_A02_09e")


class KAR_A02_09H:
    """Set the Table (Heroic)"""

    play = Buff(PLATES, "KAR_A02_09eH")


KAR_A02_09e = buff(+1, +1)
KAR_A02_09eH = buff(+2, +2)


class KAR_A02_10:
    """Pour a Round"""

    play = Draw(CONTROLLER) * Count(PLATES)


class KAR_A02_11:
    """Tossing Plates"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    play = Summon(CONTROLLER, "KAR_A02_01") * 5


##
# The Parlor: Magic Mirror


class KAR_A01_02:
    """Reflections"""

    # "Passive Hero Power Whenever a minion is played, summon a 1/1 copy of
    # it." The heroic text says "Magic Mirror summons a 1/1 copy of it": in
    # normal, the copy goes to whoever played the minion.
    tags = {enums.PASSIVE_HERO_POWER: True}
    events = Play(ALL_PLAYERS, MINION).after(
        Summon(Play.PLAYER, Copy(Play.CARD)).then(Buff(Summon.CARD, "KAR_A01_02e"))
    )


class KAR_A01_02H:
    """Reflections (Heroic)"""

    tags = {enums.PASSIVE_HERO_POWER: True}
    events = Play(ALL_PLAYERS, MINION).after(
        Summon(CONTROLLER, Copy(Play.CARD)).then(Buff(Summon.CARD, "KAR_A01_02e"))
    )


class KAR_A01_02e:
    atk = SET(1)
    max_health = SET(1)


##
# The Opera: Romulo and Julianne

ROMULO = FRIENDLY_MINIONS + IDS(["KARA_06_01", "KARA_06_01heroic"])
JULIANNE = ALL_HEROES + IDS(["KARA_06_02", "KARA_06_02heroic"])


class KARA_06_03hp:
    """True Love"""

    # "Hero Power If you don't have Romulo, summon him.": with Romulo there,
    # it has nothing to do and cannot be used.
    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    activate = Summon(CONTROLLER, "KARA_06_01")
    update = Find(ROMULO) & Refresh(SELF, {GameTag.CANT_PLAY: True})


class KARA_06_03hpheroic:
    """True Love (Heroic)"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    activate = Summon(CONTROLLER, "KARA_06_01heroic")
    update = Find(ROMULO) & Refresh(SELF, {GameTag.CANT_PLAY: True})


class KARA_06_01:
    """Romulo"""

    update = Refresh(JULIANNE, buff="KARA_06_01e")


class KARA_06_01heroic:
    """Romulo (Heroic)"""

    update = Refresh(JULIANNE, buff="KARA_06_01e")


KARA_06_01e = buff(immune=True)


##
# The Opera: Big Bad Wolf


class KARA_05_01hp:
    """Trembling"""

    # "Passive Hero Power Enemy minions are 1/1 and cost (1)."
    tags = {enums.PASSIVE_HERO_POWER: True}
    update = (
        Refresh(ENEMY_MINIONS, buff="KARA_05_01e"),
        Refresh(ENEMY_HAND + MINION, {GameTag.COST: SET(1)}),
    )


class KARA_05_01hpheroic:
    """Trembling (Heroic)"""

    # "Passive Hero Power Minions cost (1). Enemy minions are 1/1."
    tags = {enums.PASSIVE_HERO_POWER: True}
    update = (
        Refresh(ENEMY_MINIONS, buff="KARA_05_01e"),
        Refresh(IN_HAND + MINION, {GameTag.COST: SET(1)}),
    )


class KARA_05_01e:
    atk = SET(1)
    max_health = SET(1)


##
# The Opera: The Crone


def _side_of_self(left):
    """The minions to the left (or right) of the source in its controller's
    field, dormant ones excepted (as Yellow-Brick Brawl's Dorothee)."""

    def select(entities, source):
        field = source.controller.field
        if source not in field:
            return []
        i = field.index(source)
        side = field[:i] if left else field[i + 1 :]
        return [m for m in side if not m.dormant]

    return FuncSelector(select)


class KARA_04_01:
    """Dorothee"""

    # "Minions to the left have Charge. Minions to the right have Taunt." And
    # while she lives, The Crone's Twister "can't be used".
    update = (
        Refresh(_side_of_self(True), {GameTag.CHARGE: True}),
        Refresh(_side_of_self(False), {GameTag.TAUNT: True}),
        Refresh(ALL_HERO_POWERS + ID("KARA_04_02hp"), {GameTag.CANT_PLAY: True}),
    )


class KARA_04_02hp:
    """Twister"""

    # "Hero Power Deal 100 damage. Can't be used if Dorothee is alive." The
    # wiki (The Crone, Notes): "Twister always targets the player's hero, even
    # if they have Elusive." (Auto-cast: A54.)
    activate = Hit(ENEMY_HERO, 100)


##
# The Menagerie: Curator


class KARA_07_02:
    """Gallery Protection"""

    # "Passive Hero Power Your hero has Taunt."
    tags = {enums.PASSIVE_HERO_POWER: True}
    update = Refresh(FRIENDLY_HERO, buff="KARA_07_02e")


KARA_07_02e = buff(taunt=True)


class KARA_07_03:
    """Murloc Escaping!"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    play = Summon(CONTROLLER, RandomMinion(race=Race.MURLOC))


class KARA_07_03heroic:
    """Murlocs Escaping!"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    play = Summon(CONTROLLER, RandomMinion(race=Race.MURLOC)) * 2


class KARA_07_05:
    """Stampeding Beast!"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    play = Summon(CONTROLLER, RandomMinion(race=Race.BEAST))


class KARA_07_05heroic:
    """Stampeding Beast! (Heroic)"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    play = Summon(CONTROLLER, RandomMinion(race=Race.BEAST))


class KARA_07_06:
    """Demons Loose!"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    play = Summon(CONTROLLER, RandomMinion(race=Race.DEMON))


class KARA_07_06heroic:
    """Demons Loose! (Heroic)"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    play = Summon(CONTROLLER, RandomMinion(race=Race.DEMON))


class KARA_07_07:
    """Haywire Mech!"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    play = Summon(CONTROLLER, RandomMinion(race=Race.MECHANICAL))


class KARA_07_07heroic:
    """Haywire Mech! (Heroic)"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    play = Summon(CONTROLLER, RandomMinion(race=Race.MECHANICAL))


class KARA_07_08:
    """Dragons Free!"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    play = Summon(CONTROLLER, RandomMinion(race=Race.DRAGON))


class KARA_07_08heroic:
    """Dragons Free! (Heroic)"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    play = Summon(CONTROLLER, RandomMinion(race=Race.DRAGON))


##
# The Menagerie: Nightbane


class KARA_11_02:
    """Manastorm"""

    # "Passive Hero Power Players start with 10 Mana Crystals."
    tags = {enums.PASSIVE_HERO_POWER: True}
    events = GameStart().on(GainMana(ALL_PLAYERS, 10))


##
# The Menagerie: Terestian Illhoof

ILLHOOF = ALL_HEROES + IDS(["KARA_09_01", "KARA_09_01heroic"])


class KARA_09_04:
    """Dark Pact"""

    # "Passive Hero Power Only Icky Imps can damage Illhoof!": Illhoof cannot
    # be damaged; an Icky Imp's Deathrattle takes his Health all the same.
    tags = {enums.PASSIVE_HERO_POWER: True}
    update = Refresh(FRIENDLY_HERO, {GameTag.CANT_BE_DAMAGED: True})


class KARA_09_03a:
    """Icky Imp"""

    # "Deathrattle: Resummon this minion and Illhoof loses 2 Health." The
    # Health is lost past Dark Pact: it is not dealt as damage by a card
    # that could be stopped (Predamage, not Hit).
    deathrattle = Summon(CONTROLLER, "KARA_09_03a"), Predamage(ILLHOOF, 2)


class KARA_09_03a_heroic:
    """Icky Imp (Heroic)"""

    deathrattle = Summon(CONTROLLER, "KARA_09_03a_heroic"), Predamage(ILLHOOF, 2)


class KARA_09_03:
    """Many Imps!"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    play = Summon(CONTROLLER, "KARA_09_03a") * 2


class KARA_09_03heroic:
    """Many Imps! (Heroic)"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    play = Summon(CONTROLLER, "KARA_09_03a_heroic") * 2


class KARA_09_05:
    """Summon Kil'rek"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    play = Summon(CONTROLLER, "KARA_09_08")


class KARA_09_05heroic:
    """Summon Kil'rek (Heroic)"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    play = Summon(CONTROLLER, "KARA_09_08_heroic")


class KARA_09_06:
    """Shadow Volley"""

    play = Hit(ALL_MINIONS - DEMON, 3)


class KARA_09_06heroic:
    """Shadow Volley (Heroic)"""

    play = Hit(ALL_MINIONS - DEMON, 3)


class KARA_09_07:
    """Steal Life"""

    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Hit(TARGET, 5), Heal(FRIENDLY_HERO, 5)


class KARA_09_07heroic:
    """Steal Life (Heroic)"""

    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Hit(TARGET, 5), Heal(FRIENDLY_HERO, 5)


##
# The Spire: Shade of Aran


class KARA_12_02:
    """Ley Lines"""

    # "Passive Hero Power Both players have Spell Damage +3."
    tags = {enums.PASSIVE_HERO_POWER: True}
    update = Refresh(ALL_PLAYERS, {GameTag.SPELLPOWER: +3})


class KARA_12_02H:
    """Ley Lines (Heroic)"""

    tags = {enums.PASSIVE_HERO_POWER: True}
    update = Refresh(ALL_PLAYERS, {GameTag.SPELLPOWER: +5})


class KARA_12_03:
    """Flame Wreath"""

    # "Secret: When an enemy attacks, deal 5 damage to all other enemies."
    secret = Attack(ENEMY_CHARACTERS).on(
        Reveal(SELF), Hit(ENEMY_CHARACTERS - Attack.ATTACKER, 5)
    )


class KARA_12_03H:
    """Flame Wreath (Heroic)"""

    secret = Attack(ENEMY_CHARACTERS).on(
        Reveal(SELF), Hit(ENEMY_CHARACTERS - Attack.ATTACKER, 10)
    )


##
# The Spire: Netherspite


class KARA_08_02:
    """Nether Rage"""

    # "Hero Power Give your hero +3 Attack this turn." (Auto-cast: A54.)
    activate = Buff(FRIENDLY_HERO, "KARA_08_02e")


class KARA_08_02H:
    """Nether Rage (Heroic)"""

    activate = Buff(FRIENDLY_HERO, "KARA_08_02eH")


KARA_08_02e = buff(atk=3, tag_one_turn_effect=True)
KARA_08_02eH = buff(atk=8, tag_one_turn_effect=True)


class KARA_08_03:
    """Nether Breath"""

    # "Change the Health of all enemy minions to 1." (as Decimate does)
    play = Buff(ENEMY_MINIONS, "KARA_08_03e")


class KARA_08_03H:
    """Nether Breath (Heroic)"""

    play = Buff(ENEMY_MINIONS, "KARA_08_03e")


class KARA_08_03e:
    max_health = SET(1)


class KARA_08_05:
    """Terrifying Roar"""

    requirements = {
        PlayReq.REQ_ENEMY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }
    play = Bounce(TARGET)


class KARA_08_05H:
    """Terrifying Roar (Heroic)"""

    requirements = {
        PlayReq.REQ_ENEMY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }
    play = Bounce(TARGET)


def _beam(rightward):
    """The character in a portal's beam: the beam runs from the portal across
    its board (rightward from the Blue Portal, leftward from the Red one) to
    the first minion that is not dormant (the wiki: a dormant minion does not
    stop it, "carrying on to the next non-dormant minion"); with none in its
    path, it reaches Netherspite, the enemy hero."""

    def select(entities, source):
        field = source.controller.field
        if source not in field:
            return []
        i = field.index(source)
        path = field[i + 1 :] if rightward else list(reversed(field[:i]))
        for minion in path:
            if not minion.dormant:
                return [minion]
        return [source.controller.opponent.hero]

    return FuncSelector(select)


class KARA_08_06:
    """Blue Portal"""

    # A portal is permanent ("Permanent", UNTOUCHABLE): dormant for good, as
    # Yellow-Brick Brawl's Dorothee; its beam is an aura.
    tags = {GameTag.DORMANT: True}
    dormant_update = Refresh(_beam(True), buff="KARA_08_06e2")


KARA_08_06e2 = buff(heavily_armored=True)


class KARA_08_08:
    """Red Portal"""

    tags = {GameTag.DORMANT: True}
    dormant_update = Refresh(_beam(False), buff="KARA_08_08e2")


KARA_08_08e2 = buff(windfury=True)


##
# The Spire: Free Medivh! (Nazra Wildaxe, then Prince Malchezaar)
#
# The wiki (Free Medivh!, Overview): "Destroying Nazra Wildaxe removes her
# weapon and all minions from her side of the board, but does not activate
# any of their Deathrattles. As soon as the player deals lethal damage to
# Nazra Wildaxe, the player's turn ends and Prince Malchezaar appears, with
# full Health (and Armor in Heroic mode), 8 mana (10 mana in Heroic mode),
# and a fresh deck and hand of cards; notably, he always draws Twisting
# Nether at the start of his turn. [...] When Prince Malchezaar appears,
# Medivh equips the player with Atiesh."
#
# What the page does not give, and what is done here: the fresh deck is the
# boss player's `next_phase_deck` (a list of card ids the host sets: the
# wiki's deck of Prince Malchezaar), shuffled; if there is none, the boss keeps
# his deck. The fresh hand is three cards, as a first player's; the Twisting
# Nether of the deck is put on top of it afterwards, so it is the card he draws
# at the start of his first turn. The Armor of the heroic Prince is not given
# (the page says none). The player's turn is not ended at once (as for
# Kel'Thuzad): the player ends it.

TWISTING_NETHER = "EX1_312"


class HeroFallen(Evaluator):
    """The hero of the source's controller has fallen (no Health left, or
    destroyed) and is still in play: its deaths are not processed yet."""

    def check(self, source):
        hero = source.controller.hero
        return hero.zone == Zone.PLAY and (hero.health <= 0 or hero.to_be_destroyed)


class MalchezaarAppears(TargetedAction):
    """Nazra Wildaxe has fallen: Prince Malchezaar (`hero`) replaces her."""

    TARGET = ActionArg()
    HERO = ActionArg()

    def get_target_args(self, source, target):
        return [self._args[1]]

    def do(self, source, target, hero):
        if getattr(target, "malchezaar_appeared", False):
            return
        target.malchezaar_appeared = True
        log.info("%r: Prince Malchezaar appears (%s)", target, hero)
        game = source.game
        # Her minions and her weapon go, without their Deathrattles.
        gone = list(target.field)
        if target.weapon is not None:
            gone.append(target.weapon)
        # A fresh hand and a fresh deck.
        gone += list(target.hand)
        deck = getattr(target, "next_phase_deck", None)
        if deck is not None:
            gone += list(target.deck)
        for entity in gone:
            game.queue_actions(source, [Remove(entity)])
        if deck is not None:
            for id in deck:
                target.card(id, zone=Zone.DECK)
            target.shuffle_deck()
        nether = next((c for c in target.deck if c.id == TWISTING_NETHER), None)
        if nether is not None:
            target.deck.remove(nether)
        game.queue_actions(source, [Summon(target, hero), Draw(target) * 3])
        if nether is not None:
            target.deck.append(nether)
        game.queue_actions(source, [Summon(target.opponent, "KARA_13_26")])


class MalchezaarsMana(TargetedAction):
    """The start of Prince Malchezaar's first turn: his mana is 8 (10)."""

    TARGET = ActionArg()
    AMOUNT = IntArg()

    def do(self, source, target, amount):
        if getattr(target, "malchezaar_mana", False):
            return
        target.malchezaar_mana = True
        source.game.queue_actions(source, [SetMana(target, amount)])


class KARA_13_02:
    """The Horde"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    activate = Summon(CONTROLLER, "KARA_13_03")
    update = HeroFallen() & MalchezaarAppears(CONTROLLER, "KARA_13_06")


class KARA_13_02H:
    """The Horde (Heroic)"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    activate = Summon(CONTROLLER, "KARA_13_03H")
    update = HeroFallen() & MalchezaarAppears(CONTROLLER, "KARA_13_06H")


class KARA_13_13:
    """Legion"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    activate = Summon(CONTROLLER, "KARA_00_02a")
    events = OWN_TURN_BEGIN.on(MalchezaarsMana(CONTROLLER, 8))


class KARA_13_13H:
    """Legion (Heroic)"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    activate = Summon(CONTROLLER, "KARA_00_02a") * 2
    events = OWN_TURN_BEGIN.on(MalchezaarsMana(CONTROLLER, 10))


class KARA_13_11:
    """Shadow Bolt Volley"""

    play = Hit(RANDOM_ENEMY_CHARACTER * 3, 4)


class KARA_13_12:
    """Demonic Presence"""

    play = Draw(CONTROLLER) * 2, GainArmor(FRIENDLY_HERO, 10)


class KARA_13_12H:
    """Demonic Presence (Heroic)"""

    play = Draw(CONTROLLER) * 3, GainArmor(FRIENDLY_HERO, 10)


class KARA_13_26:
    """Atiesh"""

    # "After you cast a spell, summon a random minion of that Cost. Lose 1
    # Durability." (as Medivh, the Guardian's Atiesh)
    events = OWN_SPELL_PLAY.on(
        Summon(CONTROLLER, RandomMinion(cost=Attr(Play.CARD, GameTag.COST))),
        Hit(SELF, 1),
    )
