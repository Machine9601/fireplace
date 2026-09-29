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
