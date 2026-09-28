from hearthstone.enums import Zone

from ...dsl.evaluator import Evaluator
from ...logging import log
from ..utils import *


##
# The bosses in several phases (Majordomo then Ragnaros, Nefarian and
# Onyxia, Kel'Thuzad): the next phase comes while the auras refresh, before
# the deaths are processed, so a boss whose hero falls is replaced, not
# defeated.


class HeroFallen(Evaluator):
    """The hero of the source's controller has fallen (no Health left, or
    destroyed) and is still in play: its deaths are not processed yet."""

    def check(self, source):
        hero = source.controller.hero
        return hero.zone == Zone.PLAY and (hero.health <= 0 or hero.to_be_destroyed)


class ArmorBroken(Evaluator):
    """The hero of the source's controller had Armor, has none left, and is
    still standing. The source (a Hero Power) remembers the Armor it saw."""

    def check(self, source):
        hero = source.controller.hero
        if hero.armor > 0:
            source.armor_seen = True
            return False
        if not getattr(source, "armor_seen", False):
            return False
        return hero.health > 0 and not hero.to_be_destroyed


class NextPhase(TargetedAction):
    """
    The boss (target, a player) goes into its next phase: `hero` replaces its
    hero, with its own Health and its own Hero Power (the wiki: "Defeating the
    flamewaker causes him to summon forth Ragnaros the Firelord").
    """

    TARGET = ActionArg()
    HERO = ActionArg()

    def get_target_args(self, source, target):
        return [self._args[1]]

    def do(self, source, target, hero):
        log.info("%r goes into its next phase: %s", target, hero)
        source.game.queue_actions(source, [Summon(target, hero)])


##
# Hero Powers


class BRMA01_2:
    """Pile On!"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    activate = (
        Summon(CONTROLLER, RANDOM(FRIENDLY_DECK + MINION)),
        Summon(OPPONENT, RANDOM(ENEMY_DECK + MINION)),
    )


class BRMA01_2H:
    """Pile On! (Heroic)"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    activate = (
        Summon(CONTROLLER, RANDOM(FRIENDLY_DECK + MINION) * 2),
        Summon(OPPONENT, RANDOM(ENEMY_DECK + MINION)),
    )


class BRMA01_3:
    """Dark Iron Bouncer"""

    tags = {
        enums.ALWAYS_WINS_BRAWLS: True,
    }


class BRMA02_2:
    """Jeering Crowd"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    activate = Summon(CONTROLLER, "BRMA02_2t")


class BRMA02_2H:
    """Jeering Crowd (Heroic)"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    activate = Summon(CONTROLLER, "BRMA02_2t")


class BRMA03_2:
    """Power of the Firelord"""

    # "Hero Power: Deal 30 damage." (Moira Bronzebeard keeps it from being
    # used while she lives).
    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    activate = Hit(TARGET, 30)


class BRMA04_2:
    """Magma Pulse"""

    activate = Hit(ALL_MINIONS, 1)


class BRMA05_2:
    """Ignite Mana"""

    activate = (MANA(OPPONENT) <= USED_MANA(OPPONENT)) & Hit(ENEMY_HERO, 5)


class BRMA05_2H:
    """Ignite Mana (Heroic)"""

    activate = (MANA(OPPONENT) <= USED_MANA(OPPONENT)) & Hit(ENEMY_HERO, 10)


class BRMA06_2:
    """The Majordomo"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    activate = Summon(CONTROLLER, "BRMA06_4")
    # The wiki (Ragnaros the Firelord (boss)): "The encounter begins with the
    # player facing Majordomo Executus. Defeating the flamewaker causes him to
    # summon forth Ragnaros the Firelord, and the second stage of the battle
    # begins." Ragnaros (BRMA06_3) has his own 8 Health and DIE, INSECT!.
    update = HeroFallen() & NextPhase(CONTROLLER, "BRMA06_3")


class BRMA06_2H:
    """The Majordomo (Heroic)"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    activate = Summon(CONTROLLER, "BRMA06_4H")
    # Heroic: Ragnaros (BRMA06_3H) has 30 Health and DIE, INSECTS!.
    update = HeroFallen() & NextPhase(CONTROLLER, "BRMA06_3H")


class BRMA07_2:
    """ME SMASH"""

    requirements = {PlayReq.REQ_MINIMUM_ENEMY_MINIONS: 1}
    activate = Destroy(RANDOM(ENEMY_MINIONS + DAMAGED))


class BRMA07_2H:
    """ME SMASH (Heroic)"""

    activate = Destroy(RANDOM_ENEMY_MINION)


class BRMA08_2:
    """Intense Gaze"""

    update = (
        Refresh(ALL_PLAYERS, {GameTag.MAXRESOURCES: SET(1)}),
        Refresh(IN_HAND, {GameTag.COST: SET(1)}),
    )


class BRMA08_2H:
    """Intense Gaze (Heroic)"""

    update = (
        Refresh(CONTROLLER, {GameTag.MAXRESOURCES: SET(2)}),
        Refresh(OPPONENT, {GameTag.MAXRESOURCES: SET(1)}),
        Refresh(IN_HAND, {GameTag.COST: SET(1)}),
    )


class BRMA09_2:
    """Open the Gates"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    entourage = ["BRMA09_3", "BRMA09_4"]
    activate = Summon(CONTROLLER, "BRMA09_2t") * 3, Summon(
        CONTROLLER, RandomEntourage()
    )


class BRMA09_2H:
    """Open the Gates (Heroic)"""

    entourage = ["BRMA09_3H", "BRMA09_4H"]
    activate = Summon(CONTROLLER, "BRMA09_2Ht") * 3, Summon(
        CONTROLLER, RandomEntourage()
    )


class BRMA09_3:
    """Old Horde"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    entourage = ["BRMA09_2", "BRMA09_4", "BRMA09_5"]
    activate = Summon(CONTROLLER, "BRMA09_3t") * 2, Summon(
        CONTROLLER, RandomEntourage()
    )


class BRMA09_3H:
    """Old Horde (Heroic)"""

    entourage = ["BRMA09_2H", "BRMA09_4H", "BRMA09_5H"]
    activate = Summon(CONTROLLER, "BRMA09_3Ht") * 2, Summon(
        CONTROLLER, RandomEntourage()
    )


class BRMA09_4:
    """Blackwing"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    entourage = ["BRMA09_2", "BRMA09_3", "BRMA09_5"]
    activate = Summon(CONTROLLER, "BRMA09_4t"), Summon(CONTROLLER, RandomEntourage())


class BRMA09_4H:
    """Blackwing (Heroic)"""

    entourage = ["BRMA09_2H", "BRMA09_3H", "BRMA09_5H"]
    activate = Summon(CONTROLLER, "BRMA09_4Ht"), Summon(CONTROLLER, RandomEntourage())


class BRMA09_5:
    """Dismount"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    entourage = ["BRMA09_2", "BRMA09_3", "BRMA09_4"]
    activate = Summon(CONTROLLER, "BRMA09_5t"), Summon(CONTROLLER, RandomEntourage())


class BRMA09_5H:
    """Dismount (Heroic)"""

    entourage = ["BRMA09_2H", "BRMA09_3H", "BRMA09_4H"]
    activate = Summon(CONTROLLER, "BRMA09_5Ht"), Summon(CONTROLLER, RandomEntourage())


class BRMA10_3:
    """The Rookery"""

    activate = Buff(ALL_MINIONS + ID("BRMA10_4"), "BRMA10_3e"), Summon(
        CONTROLLER, "BRMA10_4"
    )


class BRMA10_3H:
    """The Rookery"""

    activate = Buff(ALL_MINIONS + ID("BRMA10_4"), "BRMA10_3e"), Summon(
        CONTROLLER, "BRMA10_4"
    )


BRMA10_3e = buff(health=1)


class BRMA11_2:
    """Essence of the Red"""

    activate = Draw(ALL_PLAYERS) * 2


class BRMA11_2H:
    """Essence of the Red (Heroic)"""

    activate = Draw(ALL_PLAYERS) * 3, GainMana(CONTROLLER, 1)


class BRMA12_2:
    """Brood Affliction"""

    entourage = ["BRMA12_6", "BRMA12_5", "BRMA12_7", "BRMA12_4", "BRMA12_3"]
    activate = Give(OPPONENT, RandomEntourage())


class BRMA12_2H:
    """Brood Affliction (Heroic)"""

    entourage = ["BRMA12_3H", "BRMA12_4H", "BRMA12_5H", "BRMA12_6H", "BRMA12_7H"]
    activate = Give(OPPONENT, RandomEntourage())


class BRMA12_10:
    """Mutation (Unused)"""

    activate = Discard(RANDOM(FRIENDLY_HAND))


# Lord Victor Nefarius (the wiki): "At the start of his first turn Lord Victor
# Nefarius will use True Form, changing into his dragon form and thus
# replacing himself with the Nefarian hero. This will also cause the boss to
# gain a significant amount of Armor, immediately set his mana to 10, and draw
# 2 additional cards for free." and "Starting with turn 3, at the start of
# each turn Ragnaros will grant the player one of the following cards at
# random. In Heroic mode this happens only once, at the start of turn 3".

RAGNAROS_HELPS = RandomID("BRMA13_5", "BRMA13_6", "BRMA13_7", "BRMA13_8")


class RagnarosHelps(TargetedAction):
    """At the start of the player's turn, from turn 3, a card from Ragnaros
    (once only in heroic)."""

    TARGET = ActionArg()

    def do(self, source, target):
        if source.game.turn < 3:
            return
        if source.id.endswith("H") and getattr(target, "ragnaros_helped", False):
            return
        target.ragnaros_helped = True
        return source.game.queue_actions(source, [Give(target, RAGNAROS_HELPS)])


class BRMA13_2:
    """True Form"""

    tags = {enums.PASSIVE_HERO_POWER: True}
    events = OWN_TURN_BEGIN.on(
        Summon(CONTROLLER, "BRMA13_3"),
        Draw(CONTROLLER) * 2,
        GainArmor(FRIENDLY_HERO, 30),
        GainMana(CONTROLLER, 10),
    )


class BRMA13_2H:
    """True Form (Heroic)"""

    tags = {enums.PASSIVE_HERO_POWER: True}
    events = OWN_TURN_BEGIN.on(
        Summon(CONTROLLER, "BRMA13_3H"),
        Draw(CONTROLLER) * 2,
        GainArmor(FRIENDLY_HERO, 30),
        GainMana(CONTROLLER, 10),
    )


class BRMA13_4:
    """Wild Magic"""

    activate = Give(CONTROLLER, RandomSpell(card_class=ENEMY_CLASS))
    events = BeginTurn(OPPONENT).on(RagnarosHelps(OPPONENT))


class BRMA13_4H:
    """Wild Magic (Heroic)"""

    activate = Give(CONTROLLER, RandomSpell(card_class=ENEMY_CLASS))
    events = BeginTurn(OPPONENT).on(RagnarosHelps(OPPONENT))


class BRMA14_2:
    """Activate Arcanotron"""

    activate = Summon(CONTROLLER, "BRMA14_3"), Summon(CONTROLLER, "BRMA14_4")


class BRMA14_2H:
    """Activate Arcanotron (Heroic)"""

    activate = Summon(CONTROLLER, "BRMA14_3"), Summon(CONTROLLER, "BRMA14_4H")


class BRMA14_4:
    """Activate Toxitron"""

    activate = Summon(CONTROLLER, "BRMA14_5"), Summon(CONTROLLER, "BRMA14_6")


class BRMA14_4H:
    """Activate Toxitron (Heroic)"""

    activate = Summon(CONTROLLER, "BRMA14_5H"), Summon(CONTROLLER, "BRMA14_6H")


class BRMA14_6:
    """Activate Electron"""

    activate = Summon(CONTROLLER, "BRMA14_7"), Summon(CONTROLLER, "BRMA14_8")


class BRMA14_6H:
    """Activate Electron (Heroic)"""

    activate = Summon(CONTROLLER, "BRMA14_7H"), Summon(CONTROLLER, "BRMA14_8H")


class BRMA14_8:
    """Activate Magmatron"""

    activate = Summon(CONTROLLER, "BRMA14_9"), Summon(CONTROLLER, "BRMA14_10")


class BRMA14_8H:
    """Activate Magmatron (Heroic)"""

    activate = Summon(CONTROLLER, "BRMA14_9H"), Summon(CONTROLLER, "BRMA14_10H")


class BRMA14_10:
    """Activate!"""

    entourage = ["BRMA14_3", "BRMA14_5", "BRMA14_7", "BRMA14_9"]
    activate = Summon(CONTROLLER, RandomEntourage())


class BRMA14_10H:
    """Activate! (Heroic)"""

    entourage = ["BRMA14_3", "BRMA14_5H", "BRMA14_7H", "BRMA14_9H"]
    activate = Summon(CONTROLLER, RandomEntourage())


class BRMA15_2:
    """The Alchemist"""

    events = Summon(ALL_PLAYERS, MINION).on(Buff(Summon.CARD, "BRMA15_2e"))


@custom_card
class BRMA15_2e(AttackHealthSwapBuff()):
    # Not in CardDefs.xml
    tags = {
        GameTag.CARDNAME: "The Alchemist Attack/Health Swap Buff",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }


class BRMA15_2H:
    """The Alchemist (Heroic)"""

    events = (
        Summon(ALL_PLAYERS, MINION).on(Buff(Summon.CARD, "BRMA15_2e")),
        Summon(CONTROLLER, MINION).on(Buff(Summon.CARD, "BRMA15_2He")),
    )


# Potion of Might (The Alchemist)
BRMA15_2He = buff(+2, +2)


class BRMA16_2:
    """Echolocate"""

    activate = Summon(CONTROLLER, "BRMA16_5")


class BRMA16_2H:
    """Echolocate (Heroic)"""

    activate = Summon(CONTROLLER, "BRMA16_5")


# Nefarian (Hidden Laboratory), "a three-stage fight, with the first and third
# stages fought against Nefarian, and the second against Nefarian's sister
# Onyxia" (the wiki). The guides: Nefarian starts with 10 Armor (30 in
# heroic); once it is gone, Onyxia (15 Health, 30 in heroic) takes his place
# and wields Onyxiclaw; "When she dies, Nefarian returns with the same health
# he had before Onyxia came into play. When Nefarian comes back in play, he
# clears the board." The wiki: "If the player deals enough damage to break
# Nefarian's armor and kill all 30 of his hitpoints in a single hit in Stage
# 1, the game skips both Stage 2 and 3".


class OnyxiaRises(TargetedAction):
    """Stage 2: Onyxia replaces Nefarian (target, the boss player)."""

    TARGET = ActionArg()

    def do(self, source, target):
        if getattr(target, "nefarian_stage", 1) != 1:
            return
        target.nefarian_stage = 2
        target.nefarian_damage = target.hero.damage
        heroic = source.id.endswith("H")
        source.game.queue_actions(
            source,
            [
                Summon(target, "BRMA17_3H" if heroic else "BRMA17_3"),
                Summon(target, "BRMA17_9"),
            ],
        )


class NefarianReturns(TargetedAction):
    """Stage 3: Onyxia has fallen, Nefarian returns and clears the board."""

    TARGET = ActionArg()

    def do(self, source, target):
        if getattr(target, "nefarian_stage", 1) != 2:
            return
        target.nefarian_stage = 3
        heroic = source.id.endswith("H")
        source.game.queue_actions(
            source,
            [Destroy(ALL_MINIONS), Summon(target, "BRMA17_2H" if heroic else "BRMA17_2")],
        )
        target.hero.damage = getattr(target, "nefarian_damage", 0)


class NefarianStrikes(TargetedAction):
    """
    Onyxia's Hero Power, auto-cast: "Nefarian rains fire from above!" The
    wiki's table: 1, 2, 1, 3, 1, 4 and 0 fireballs on the first seven turns,
    then 20 every turn.
    """

    TARGET = ActionArg()
    FIREBALLS = (1, 2, 1, 3, 1, 4, 0)

    def do(self, source, target):
        turn = getattr(target, "strikes", 0)
        target.strikes = turn + 1
        count = self.FIREBALLS[turn] if turn < len(self.FIREBALLS) else 20
        if count:
            source.game.queue_actions(source, [Hit(ENEMY_HERO, 1) * count])


class BRMA17_5:
    """Bone Minions"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    activate = Summon(CONTROLLER, "BRMA17_6") * 2
    update = ArmorBroken() & OnyxiaRises(CONTROLLER)


class BRMA17_5H:
    """Bone Minions (Heroic)"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    activate = Summon(CONTROLLER, "BRMA17_6H") * 2
    update = ArmorBroken() & OnyxiaRises(CONTROLLER)


class BRMA17_8:
    """Nefarian Strikes!"""

    tags = {enums.PASSIVE_HERO_POWER: True}
    events = OWN_TURN_BEGIN.on(NefarianStrikes(SELF))
    update = HeroFallen() & NefarianReturns(CONTROLLER)


class BRMA17_8H:
    """Nefarian Strikes! (Heroic)"""

    tags = {enums.PASSIVE_HERO_POWER: True}
    events = OWN_TURN_BEGIN.on(NefarianStrikes(SELF))
    update = HeroFallen() & NefarianReturns(CONTROLLER)


##
# Minions


class BRMA03_3:
    """Moira Bronzebeard"""

    update = Refresh(ALL_HERO_POWERS + ID("BRMA03_2"), {GameTag.CANT_PLAY: True})


class BRMA03_3H:
    """Moira Bronzebeard (Heroic)"""

    update = Refresh(ALL_HERO_POWERS + ID("BRMA03_2"), {GameTag.CANT_PLAY: True})


class BRMA10_4:
    """Corrupted Egg"""

    update = (CURRENT_HEALTH(SELF) >= 4) & (
        Destroy(SELF),
        Summon(CONTROLLER, "BRMA10_5"),
    )


class BRMA10_4H:
    """Corrupted Egg (Heroic)"""

    update = (CURRENT_HEALTH(SELF) >= 5) & (
        Destroy(SELF),
        Summon(CONTROLLER, "BRMA10_5H"),
    )


class BRMA04_3:
    """Firesworn"""

    deathrattle = Hit(ENEMY_HERO, Count(ID("BRMA04_3") + KILLED_THIS_TURN))


class BRMA04_3H:
    """Firesworn (Heroic)"""

    deathrattle = Hit(ENEMY_HERO, Count(ID("BRMA04_3H") + KILLED_THIS_TURN))


class BRMA12_8t:
    """Chromatic Dragonkin"""

    events = Play(OPPONENT, SPELL).on(Buff(SELF, "BRMA12_8te"))


BRMA12_8te = buff(+2, +2)


class BRMA13_5:
    """Son of the Flame"""

    requirements = {PlayReq.REQ_TARGET_IF_AVAILABLE: 0}
    play = Hit(TARGET, 6)


##
# Spells


class BRMA_01:
    """Flameheart"""

    play = Draw(CONTROLLER) * 2, GainArmor(FRIENDLY_HERO, 4)


class BRMA01_4:
    """Get 'em!"""

    play = Summon(CONTROLLER, "BRMA01_4t") * 4


class BRMA05_3:
    """Living Bomb"""

    requirements = {
        PlayReq.REQ_ENEMY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }
    play = Buff(TARGET, "BRMA05_3e")


class BRMA05_3e:
    events = OWN_TURN_BEGIN.on(Hit(ENEMY_CHARACTERS, 5))


class BRMA05_3H:
    """Living Bomb (Heroic)"""

    requirements = {
        PlayReq.REQ_ENEMY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }
    play = Buff(TARGET, "BRMA05_3He")


class BRMA05_3He:
    events = OWN_TURN_BEGIN.on(Hit(ENEMY_CHARACTERS, 10))


class BRMA07_3:
    """TIME FOR SMASH"""

    play = Hit(RANDOM_ENEMY_MINION, 5), GainArmor(FRIENDLY_HERO, 5)


class BRMA08_3:
    """Drakkisath's Command"""

    requirements = {PlayReq.REQ_MINION_TARGET: 0, PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Destroy(TARGET), GainArmor(FRIENDLY_HERO, 10)


class BRMA09_6:
    """The True Warchief"""

    requirements = {
        PlayReq.REQ_LEGENDARY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }
    play = Destroy(TARGET)


class BRMA04_4:
    """Rock Out"""

    play = Summon(CONTROLLER, "BRMA04_3") * 3


class BRMA04_4H:
    """Rock Out (Heroic)"""

    play = Summon(CONTROLLER, "BRMA04_3H") * 3


class BRMA11_3:
    """Burning Adrenaline"""

    play = Hit(ENEMY_HERO, 2)


class BRMA12_8:
    """Chromatic Mutation (Unused)"""

    requirements = {PlayReq.REQ_MINION_TARGET: 0, PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Morph(TARGET, "BRMA12_8t")


class BRMA14_11:
    """Recharge"""

    play = FillMana(CONTROLLER, USED_MANA(CONTROLLER))


class BRMA13_8:
    """DIE, INSECT!"""

    play = Hit(RANDOM_ENEMY_CHARACTER, 8)


class BRMA15_3:
    """Release the Aberrations!"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    play = Summon(CONTROLLER, "BRMA15_4") * 3


class BRMA14_3:
    """Arcanotron"""

    update = Refresh(ALL_PLAYERS, {GameTag.SPELLPOWER: +2})


class BRMA14_5:
    """Toxitron"""

    events = OWN_TURN_BEGIN.on(Hit(ALL_MINIONS - SELF, 1))


class BRMA14_5H:
    """Toxitron (Heroic)"""

    events = OWN_TURN_BEGIN.on(Hit(ALL_MINIONS - SELF, 1))


class BRMA14_7:
    """Electron"""

    update = Refresh(IN_HAND + SPELL, {GameTag.COST: -3})


class BRMA14_7H:
    """Electron (Heroic)"""

    update = Refresh(IN_HAND + SPELL, {GameTag.COST: -3})


class BRMA14_9:
    """Magmatron"""

    events = Play().on(Hit(ALL_HEROES + CONTROLLED_BY(Play.PLAYER), 2))


class BRMA14_9H:
    """Magmatron"""

    events = Play().on(Hit(ALL_HEROES + CONTROLLED_BY(Play.PLAYER), 2))


class BRMA16_3:
    """Sonic Breath"""

    requirements = {
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_WEAPON_EQUIPPED: 0,
    }
    play = Hit(TARGET, 3), Buff(FRIENDLY_WEAPON, "BRMA16_3e")


BRMA16_3e = buff(atk=3)


class BRMA16_4:
    """Reverberating Gong"""

    requirements = {PlayReq.REQ_ENEMY_WEAPON_EQUIPPED: 0}
    play = Destroy(ENEMY_WEAPON)


class BRMA17_4:
    """LAVA!"""

    play = Hit(ALL_MINIONS, 2)


##
# Weapons


class BRMA10_6:
    """Razorgore's Claws (Unused)"""

    events = Death(MINION + ID("BRMA10_4")).on(Buff(SELF, "BRMA10_6e"))


BRMA10_6e = buff(atk=1)


class BRMA16_5:
    """Dragonteeth"""

    events = Play(OPPONENT).on(Buff(SELF, "BRMA16_5e"))


BRMA16_5e = buff(atk=1)


##
# Brood Afflictions (Chromaggus)


class BRMA12_3:
    """Brood Affliction: Red"""

    class Hand:
        events = OWN_TURN_BEGIN.on(Hit(FRIENDLY_HERO, 1))


class BRMA12_3H:
    """Brood Affliction: Red (Heroic)"""

    class Hand:
        events = OWN_TURN_BEGIN.on(Hit(FRIENDLY_HERO, 3))


class BRMA12_4:
    """Brood Affliction: Green"""

    class Hand:
        events = OWN_TURN_BEGIN.on(Heal(ENEMY_HERO, 2))


class BRMA12_4H:
    """Brood Affliction: Green (Heroic)"""

    class Hand:
        events = OWN_TURN_BEGIN.on(Heal(ENEMY_HERO, 6))


class BRMA12_5:
    """Brood Affliction: Blue"""

    class Hand:
        update = Refresh(ENEMY_HAND + SPELL, {GameTag.COST: -1})


class BRMA12_5H:
    """Brood Affliction: Blue (Heroic)"""

    class Hand:
        update = Refresh(ENEMY_HAND + SPELL, {GameTag.COST: -3})


class BRMA12_6:
    """Brood Affliction: Black"""

    class Hand:
        events = Draw(OPPONENT).on(Give(OPPONENT, Copy(Draw.CARD)))


class BRMA12_6H:
    """Brood Affliction: Black (Heroic)"""

    class Hand:
        events = Draw(OPPONENT).on(Give(OPPONENT, Copy(Draw.CARD)))


class BRMA12_7:
    """Brood Affliction: Bronze"""

    class Hand:
        update = Refresh(ENEMY_HAND + MINION, {GameTag.COST: -1})


class BRMA12_7H:
    """Brood Affliction: Bronze (Heroic)"""

    class Hand:
        update = Refresh(ENEMY_HAND + MINION, {GameTag.COST: -3})
