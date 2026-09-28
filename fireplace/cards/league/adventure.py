from hearthstone.enums import PlayState, Zone

from ...dsl.evaluator import Evaluator
from ...logging import log
from ..utils import *

##
# Zinaar

RandomWish = RandomID("LOEA02_03", "LOEA02_04", "LOEA02_05", "LOEA02_06", "LOEA02_10")


class LOEA02_02:
    """Djinn’s Intuition"""

    activate = Draw(CONTROLLER), Give(OPPONENT, RandomWish)


class LOEA02_02h:
    activate = Draw(CONTROLLER), GainMana(CONTROLLER, 1), Give(OPPONENT, RandomWish)


class LOEA02_03:
    """Wish for Power"""

    play = DISCOVER(RandomSpell())


class LOEA02_04:
    """Wish for Valor"""

    play = DISCOVER(RandomCollectible(cost=4))


class LOEA02_05:
    """Wish for Glory"""

    play = DISCOVER(RandomMinion())


class LOEA02_06:
    """Wish for More Wishes"""

    play = Give(CONTROLLER, RandomWish) * 2


class LOEA02_10:
    """Wish for Companionship"""

    play = DISCOVER(RandomID("NEW1_032", "NEW1_033", "NEW1_034"))


class LOEA02_10a:
    """Leokk (Unused)"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    update = Refresh(FRIENDLY_MINIONS - SELF, buff="NEW1_033o")


##
# Sun Raider Phaerix


class LOEA01_02:
    """Blessings of the Sun"""

    update = (
        Find(FRIENDLY_MINIONS + ID("LOEA01_11"))
        & (Refresh(FRIENDLY_HERO, {GameTag.CANT_BE_DAMAGED: True})),
        Find(ENEMY_MINIONS + ID("LOEA01_11"))
        & (Refresh(ENEMY_HERO, {GameTag.CANT_BE_DAMAGED: True})),
    )


class LOEA01_02h:
    events = Summon(CONTROLLER, ID("LOEA01_11h")).on(Buff(Summon.CARD, "LOEA01_11he"))
    update = Find(FRIENDLY_MINIONS + ID("LOEA01_11h")) & (
        Refresh(FRIENDLY_HERO, {GameTag.CANT_BE_DAMAGED: True})
    )


class LOEA01_11:
    """Rod of the Sun"""

    deathrattle = Summon(OPPONENT, "LOEA01_11")


class LOEA01_11h:
    deathrattle = Summon(OPPONENT, "LOEA01_11h")


LOEA01_11he = buff(+3, +3)


class LOEA01_12:
    """Tol'vir Hoplite"""

    deathrattle = Hit(ALL_HEROES, 5)


class LOEA01_12h:
    deathrattle = Hit(ALL_HEROES, 5)


##
# The escapes: Temple Escape and Mine Cart Rush
#
# The wiki (Temple Escape, Mine Cart Rush): "the hero is Immune and does not
# have a Health count. Rather than defeating the hero, the player has to
# survive until the "turns to escape" count reaches 0. The "turns to escape"
# count goes down at the end of the boss' turn." Both last 10 turns. The
# count lives on the boss's Hero Power (TAG_SCRIPT_DATA_NUM_1, `data_num_1`),
# which acts by itself ("Auto-cast"): it is never used.

TURNS_TO_ESCAPE = 10


class EscapeCountdown(TargetedAction):
    """
    Get the player `amount` turns closer to the Exit: the count of the escape
    Hero Power `target` goes down; at 0, the player has escaped and the boss
    (its controller) loses.
    """

    TARGET = ActionArg()
    AMOUNT = IntArg()

    def do(self, source, target, amount):
        if target.data_num_1 <= 0:
            return
        target.data_num_1 = max(0, target.data_num_1 - amount)
        log.info("%r: %i turns to escape", target, target.data_num_1)
        if target.data_num_1 == 0:
            target.controller.playstate = PlayState.LOSING
            source.game.check_for_end_game()


class PathChoice(Choice):
    """
    A path of Temple Escape: the player chooses one of two spells, which is
    cast for him at once (no Mana, never through his hand); the other one is
    gone.
    """

    def choose(self, card):
        super().choose(card)
        for other in self.cards:
            if other is not card:
                other.zone = Zone.REMOVEDFROMGAME
        self.game.cheat_action(self.player, [CastSpell(card)])
        if card.zone in (Zone.PLAY, Zone.SETASIDE, Zone.GRAVEYARD):
            card.zone = Zone.REMOVEDFROMGAME


class ChooseYourPath(TargetedAction):
    """The player `target` chooses between the two paths of `card`."""

    TARGET = ActionArg()
    CARD = ActionArg()

    PATHS = {
        "LOEA04_28": ("LOEA04_28a", "LOEA04_28b"),
        "LOEA04_06": ("LOEA04_06a", "LOEA04_06b"),
        "LOEA04_29": ("LOEA04_29a", "LOEA04_29b"),
        "LOEA04_30": ("LOEA04_30a", "LOEA04_31b"),
    }

    def get_target_args(self, source, target):
        return [self._args[1]]

    def do(self, source, target, card):
        options = [target.card(id, source=target) for id in self.PATHS[card]]
        return source.game.queue_actions(source, [PathChoice(target, options)])


# Temple Escape, "Event order" (the wiki): what the boss's turn N brings, in
# normal and heroic, and the path the player then chooses at the start of
# his turn. Turn 3 also puts a Rolling Boulder on the right of the player's
# side; turn 5 destroys every minion. "Take the Shortcut" gets the player 1
# turn closer to the Exit, so the next turn (the Seething Statue) is skipped.
TEMPLE_ESCAPE_EVENTS = {
    1: (["FP1_001"], ["CS2_200"], "LOEA04_28"),
    2: (["CS2_119"], ["LOE_009"], "LOEA04_06"),
    3: (["LOEA04_13bt"], ["LOEA04_13bth", "LOEA04_13bth"], None),
    4: ([], [], "LOEA04_29"),
    5: ([], [], None),
    6: (["LOEA04_24"], ["LOEA04_24h", "LOEA04_24h"], None),
    7: (["LOE_009"], ["LOE_009"], "LOEA04_30"),
    8: (["LOEA04_25"], ["LOEA04_25h"], None),
    9: (["LOEA04_23"] * 2, ["LOEA04_23h"] * 3, None),
}


class TempleEscapeTurn(TargetedAction):
    """The boss's turn of Temple Escape: its obstacles, then the path to come."""

    TARGET = ActionArg()

    def do(self, source, target):
        step = TURNS_TO_ESCAPE + 1 - target.data_num_1
        event = TEMPLE_ESCAPE_EVENTS.get(step)
        target.escape_path = None
        if event is None:
            return
        normal, heroic, path = event
        actions = []
        if step == 5:
            actions.append(Destroy(ALL_MINIONS))
        for id in heroic if target.id.endswith("h") else normal:
            actions.append(Summon(CONTROLLER, id))
        if step == 3:
            actions.append(Summon(OPPONENT, "LOE_024t"))
        target.escape_path = path
        if actions:
            return source.game.queue_actions(source, actions)


class TempleEscapePath(TargetedAction):
    """At the start of the player's turn, the path the last obstacle opened."""

    TARGET = ActionArg()

    def do(self, source, target):
        path = getattr(target, "escape_path", None)
        target.escape_path = None
        if path is not None:
            return source.game.queue_actions(
                source, [ChooseYourPath(target.controller.opponent, path)]
            )


class LOEA04_02:
    """Escape!"""

    tags = {
        enums.PASSIVE_HERO_POWER: True,
        GameTag.TAG_SCRIPT_DATA_NUM_1: TURNS_TO_ESCAPE,
    }
    update = Refresh(FRIENDLY_HERO, {GameTag.CANT_BE_DAMAGED: True})
    events = (
        OWN_TURN_BEGIN.on(TempleEscapeTurn(SELF)),
        BeginTurn(OPPONENT).on(TempleEscapePath(SELF)),
        OWN_TURN_END.on(EscapeCountdown(SELF, 1)),
    )


class LOEA04_02h:
    """Escape! (Heroic)"""

    tags = {
        enums.PASSIVE_HERO_POWER: True,
        GameTag.TAG_SCRIPT_DATA_NUM_1: TURNS_TO_ESCAPE,
    }
    update = Refresh(FRIENDLY_HERO, {GameTag.CANT_BE_DAMAGED: True})
    events = (
        OWN_TURN_BEGIN.on(TempleEscapeTurn(SELF)),
        BeginTurn(OPPONENT).on(TempleEscapePath(SELF)),
        OWN_TURN_END.on(EscapeCountdown(SELF, 1)),
    )


class LOEA04_06:
    """Pit of Spikes"""

    choose = ("LOEA04_06a", "LOEA04_06b")


class LOEA04_06a:
    """Swing Across"""

    play = COINFLIP & Hit(FRIENDLY_HERO, 10)


class LOEA04_06b:
    """Walk Across Gingerly"""

    play = Hit(FRIENDLY_HERO, 5)


class LOEA04_28:
    """A Glowing Pool"""

    choose = ("LOEA04_28a", "LOEA04_28b")


class LOEA04_28a:
    """Drink Deeply"""

    play = Draw(CONTROLLER)


class LOEA04_28b:
    """Wade Through"""

    play = GainMana(CONTROLLER, 1)


class LOEA04_29:
    """The Eye"""

    choose = ("LOEA04_29a", "LOEA04_29b")


class LOEA04_29a:
    """Touch It"""

    # The ruby of the statue: "Restore 10 Health to your hero." and the
    # Animated Statue awakens on the boss's side ("You've disturbed the
    # ancient statue...", the wiki's Temple Escape: "Animated Statue appears
    # [...] I think he wants his gem back!").
    play = Heal(FRIENDLY_HERO, 10), Summon(OPPONENT, "LOEA04_27")


class LOEA04_29b:
    """Investigate the Runes"""

    play = Draw(CONTROLLER) * 2


class LOEA04_30:
    """The Darkness"""

    choose = ("LOEA04_30a", "LOEA04_31b")


class LOEA04_30a:
    """Take the Shortcut"""

    # "Get 1 turn closer to the Exit! Encounter a 7/7 War Golem."
    play = Summon(OPPONENT, "CS2_186"), EscapeCountdown(ENEMY_HERO_POWER, 1)


class LOEA04_31b:
    """No Way!"""

    pass


class LOEA04_25:
    """Seething Statue"""

    events = OWN_TURN_END.on(Hit(ENEMY_CHARACTERS, 2))


class LOEA04_25h:
    events = OWN_TURN_END.on(Hit(ENEMY_CHARACTERS, 5))


class LOE_024t:
    """Rolling Boulder"""

    events = OWN_TURN_END.on(Destroy(LEFT_OF(SELF)))


##
# Chieftain Scarvash


class LOEA05_02:
    """Trogg Hate Minions!"""

    # "Passive Hero Power: Enemy minions cost (2) more. Swap at the start of
    # your turn." Scarvash starts with it; at the start of each of his turns
    # it becomes Trogg Hate Spells! (LOEA05_03), which becomes Trogg Hate
    # Minions! again (LOEA05_02a, the same power after a swap), and so on.
    update = Refresh(ENEMY_HAND + MINION, {GameTag.COST: +2})
    events = OWN_TURN_BEGIN.on(Summon(CONTROLLER, "LOEA05_03"))


class LOEA05_02a:
    update = Refresh(ENEMY_HAND + MINION, {GameTag.COST: +2})
    events = OWN_TURN_BEGIN.on(Summon(CONTROLLER, "LOEA05_03"))


class LOEA05_02h:
    update = Refresh(ENEMY_HAND + MINION, {GameTag.COST: SET(11)})
    events = OWN_TURN_BEGIN.on(Summon(CONTROLLER, "LOEA05_03h"))


class LOEA05_02ha:
    update = Refresh(ENEMY_HAND + MINION, {GameTag.COST: SET(11)})
    events = OWN_TURN_BEGIN.on(Summon(CONTROLLER, "LOEA05_03h"))


class LOEA05_03:
    """Trogg Hate Spells!"""

    update = Refresh(ENEMY_HAND + SPELL, {GameTag.COST: +2})
    events = OWN_TURN_BEGIN.on(Summon(CONTROLLER, "LOEA05_02a"))


class LOEA05_03h:
    update = Refresh(ENEMY_HAND + SPELL, {GameTag.COST: SET(11)})
    events = OWN_TURN_BEGIN.on(Summon(CONTROLLER, "LOEA05_02ha"))


##
# Mine Cart Rush
#
# The wiki (Mine Cart Rush): "The boss has a deck, but does not play cards or
# draw cards at the start of the turn. The boss uses its Hero Power Flee the
# Mine! at the start of every turn to summon minions." It "summons 2 of the
# below minions onto the boss' side of the board (3 minions the first time it
# is used). The selection is random, although the chances are uneven, with
# the more powerful options more common in Heroic mode. Debris is rarely
# seen, and excluded from Heroic mode." The player "is the Mine Cart, their
# Hero Power is Throw Rocks, they are locked at two Mana Crystals".
# The wiki gives no odds: Debris is 1 in 10 in normal, the others even.

MINE_CART_NORMAL = RandomID(
    *(["LOEA07_09"] * 3 + ["LOEA07_12"] * 3 + ["LOEA07_14"] * 3 + ["LOEA07_11"])
)
MINE_CART_HEROIC = RandomID("LOEA07_09", "LOEA07_12", "LOEA07_14")


class MineCartTurn(TargetedAction):
    """The boss's turn of Mine Cart Rush: the troggs catch up."""

    TARGET = ActionArg()

    def do(self, source, target):
        first = not getattr(target, "mine_cart_started", False)
        target.mine_cart_started = True
        pool = MINE_CART_HEROIC if target.id.endswith("h") else MINE_CART_NORMAL
        return source.game.queue_actions(
            source, [Summon(CONTROLLER, pool) * (3 if first else 2)]
        )


class LockedMineCart(TargetedAction):
    """The Mine Cart is locked at two Mana Crystals, from its first turn."""

    TARGET = ActionArg()

    def do(self, source, target):
        target.max_mana = 2


class LOEA07_03:
    """Flee the Mine!"""

    tags = {
        enums.PASSIVE_HERO_POWER: True,
        GameTag.TAG_SCRIPT_DATA_NUM_1: TURNS_TO_ESCAPE,
    }
    update = (
        Refresh(FRIENDLY_HERO, {GameTag.CANT_BE_DAMAGED: True}),
    )
    events = (
        OWN_TURN_BEGIN.on(MineCartTurn(SELF)),
        BeginTurn(OPPONENT).on(LockedMineCart(OPPONENT)),
        OWN_TURN_END.on(EscapeCountdown(SELF, 1)),
    )


class LOEA07_03h:
    """Flee the Mine! (Heroic)"""

    tags = {
        enums.PASSIVE_HERO_POWER: True,
        GameTag.TAG_SCRIPT_DATA_NUM_1: TURNS_TO_ESCAPE,
    }
    update = (
        Refresh(FRIENDLY_HERO, {GameTag.CANT_BE_DAMAGED: True}),
    )
    events = (
        OWN_TURN_BEGIN.on(MineCartTurn(SELF)),
        BeginTurn(OPPONENT).on(LockedMineCart(OPPONENT)),
        OWN_TURN_END.on(EscapeCountdown(SELF, 1)),
    )


class LOEA07_21:
    """Barrel Forward"""

    # "Get 1 turn closer to the Exit!"
    play = EscapeCountdown(ENEMY_HERO_POWER, 1)


class LOEA07_29:
    """Throw Rocks"""

    activate = Hit(RANDOM_ENEMY_MINION, 3)


class LOEA07_18:
    """Dynamite"""

    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Hit(TARGET, 10)


class LOEA07_20:
    """Boom!"""

    play = Hit(ENEMY_MINIONS, 3)


class LOEA07_26:
    """Consult Brann"""

    play = Draw(CONTROLLER) * 3


class LOEA07_28:
    """Repairs"""

    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Heal(TARGET, 10)


##
# Archaedas


class LOEA06_02:
    """Stonesculpting"""

    activate = Summon(ALL_PLAYERS, "LOEA06_02t")


class LOEA06_02h:
    activate = Summon(CONTROLLER, "LOEA06_02t"), Summon(OPPONENT, "LOEA06_02th")


class LOEA06_03:
    """Animate Earthen"""

    requirements = {PlayReq.REQ_MINIMUM_TOTAL_MINIONS: 1}
    play = Buff(FRIENDLY_MINIONS, "LOEA06_03e")


LOEA06_03e = buff(+1, +1, taunt=True)


class LOEA06_03h:
    play = Buff(FRIENDLY_MINIONS, "LOEA06_03eh")


LOEA06_03eh = buff(+3, +3, taunt=True)


class LOEA06_04:
    """Shattering Spree"""

    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = (
        Hit(TARGET, Count(ALL_MINIONS + ID("LOEA06_02t"))),
        Destroy(ALL_MINIONS + ID("LOEA06_02t")),
    )


class LOEA06_04h:
    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = (
        Hit(TARGET, Count(ALL_MINIONS + ID("LOEA06_02th")) * 3),
        Destroy(ALL_MINIONS + ID("LOEA06_02th")),
    )


##
# Lord Slitherspear

HUNGRY_NAGA = (
    ID("LOEA09_5")
    | ID("LOEA09_5H")
    | ID("LOEA09_10")
    | ID("LOEA09_11")
    | ID("LOEA09_12")
    | ID("LOEA09_13")
)


class LOEA09_2:
    """Enraged!"""

    activate = Buff(FRIENDLY_HERO, "LOEA09_2e")


LOEA09_2e = buff(atk=2)


class LOEA09_2H:
    """Enraged! (Heroic)"""

    activate = Buff(FRIENDLY_HERO, "LOEA09_2e")


LOEA09_2eH = buff(atk=5)


class LOEA09_3:
    """Getting Hungry"""

    activate = Summon(CONTROLLER, "LOEA09_5").then(
        Buff(Summon.CARD, "LOEA09_3a")
        * Attr(CONTROLLER, GameTag.NUM_TIMES_HERO_POWER_USED_THIS_GAME)
    )


LOEA09_3a = buff(atk=1)


class LOEA09_3H:
    """Getting Hungry (Heroic)"""

    activate = Summon(CONTROLLER, "LOEA09_5").then(
        Buff(Summon.CARD, "LOEA09_3aH")
        * Attr(CONTROLLER, GameTag.NUM_TIMES_HERO_POWER_USED_THIS_GAME)
    )


LOEA09_3aH = buff(+1, +1)


class LOEA09_3b:
    """Getting Hungry (Unused versions)"""

    activate = Summon(CONTROLLER, "LOEA09_11")


class LOEA09_3c:
    activate = Summon(CONTROLLER, "LOEA09_10")


class LOEA09_3d:
    activate = Summon(CONTROLLER, "LOEA09_13")


class LOEA09_6:
    """Slithering Archer"""

    requirements = {PlayReq.REQ_NONSELF_TARGET: 0, PlayReq.REQ_TARGET_IF_AVAILABLE: 0}
    play = Hit(TARGET, 1)


class LOEA09_6H:
    """Slithering Archer (Heroic)"""

    play = Hit(ENEMY_MINIONS, 2)


class LOEA09_7:
    """Cauldron"""

    deathrattle = Give(OPPONENT, "LOE_076"), Summon(CONTROLLER, "LOEA09_2")


class LOEA09_7H:
    """Cauldron (Unused)"""

    deathrattle = Give(OPPONENT, "LOE_076"), Summon(CONTROLLER, "LOEA09_2H")


class LOEA09_9:
    """Naga Repellent"""

    play = Destroy(ALL_MINIONS + HUNGRY_NAGA)


class LOEA09_9H:
    """Naga Repellent (Heroic)"""

    play = Buff(ALL_MINIONS + HUNGRY_NAGA, "EX1_360e")


##
# Giantfin


class LOEA10_2:
    """Mrglmrgl MRGL!"""

    activate = DrawUntil(CONTROLLER, Count(ENEMY_HAND))


class LOEA10_2H:
    """Mrglmrgl MRGL! (Heroic)"""

    activate = Draw(CONTROLLER) * 2


class LOEA10_5:
    """Mrgl Mrgl Nyah Nyah"""

    play = Summon(CONTROLLER, Copy(RANDOM(KILLED + MURLOC) * 5))


class LOEA10_5H:
    """Mrgl Mrgl Nyah Nyah (Heroic)"""

    play = Summon(CONTROLLER, Copy(RANDOM(KILLED + MURLOC) * 5))


##
# Lady Naz'jar


class LOEA12_2:
    """Pearl of the Tides"""

    # "At the end of your turn, replace all minions with new ones that cost
    # (1) more." It acts by itself, at the end of her turn: it is not used.
    tags = {enums.PASSIVE_HERO_POWER: True}
    events = OWN_TURN_END.on(Evolve(ALL_MINIONS, 1))


class LOEA12_2H:
    """Pearl of the Tides (Heroic)"""

    # "At the end of your turn, replace all minions with new ones. Yours cost
    # (1) more."
    tags = {enums.PASSIVE_HERO_POWER: True}
    events = OWN_TURN_END.on(Evolve(FRIENDLY_MINIONS, 1), Evolve(ENEMY_MINIONS, 0))


##
# Skelesaurus Hex


class LOEA13_2:
    """Ancient Power"""

    activate = Give(ALL_PLAYERS, RandomCollectible()).then(Buff(Give.CARD, "LOEA13_2e"))


@custom_card
class LOEA13_2e:
    # Not in CardDefs.xml: "It costs (0)." (Ancient Power, Skelesaurus Hex)
    tags = {
        GameTag.CARDNAME: "Ancient Power",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
    cost = SET(0)
    events = REMOVED_IN_PLAY


class LOEA13_2H:
    """Ancient Power (Heroic)"""

    activate = Give(CONTROLLER, RandomCollectible()).then(Buff(Give.CARD, "LOEA13_2e"))


##
# The Steel Sentinel


class LOEA14_2:
    """Platemail Armor"""

    update = Refresh(FRIENDLY_HERO, {GameTag.HEAVILY_ARMORED: True})


class LOEA14_2H:
    """Platemail Armor (Heroic)"""

    update = Refresh(FRIENDLY_CHARACTERS, {GameTag.HEAVILY_ARMORED: True})


##
# Arch-Thief Rafaam


class LOEA15_2:
    """Unstable Portal"""

    activate = Give(CONTROLLER, RandomMinion()).then(Buff(Give.CARD, "GVG_003e"))


class LOEA15_2H:
    """Unstable Portal (Heroic)"""

    activate = Give(CONTROLLER, RandomMinion()).then(Buff(Give.CARD, "GVG_003e"))


class LOEA09_4:
    """Rare Spear"""

    events = Play(OPPONENT, RARE).on(Buff(SELF, "EX1_409e"))


class LOEA09_4H:
    """Rare Spear (Heroic)"""

    events = Play(OPPONENT, RARE).on(Buff(SELF, "EX1_409e"))


##
# Rafaam Unleashed


# The wiki (Rafaam Unleashed): "Staff of Origination takes 3 turns to charge.
# Once fully charged, at the start of the turn it will summon one of the
# random boss minions listed below, but lose its normal Immune effect. The
# next turn the Staff will return to normal and begin the cycle afresh."
# Rafaam is Immune while the staff charges: he can only be hurt from the turn
# the staff fires until the start of his next turn.

RAFAAM_BOSSES = (
    "LOEA16_18", "LOEA16_19", "LOEA16_21", "LOEA16_22", "LOEA16_23",
    "LOEA16_24", "LOEA16_25", "LOEA16_26", "LOEA16_27",
)


class StaffOfOrigination(TargetedAction):
    """The staff (target) charges at the start of Rafaam's turn; the fourth
    turn, it summons a boss and Rafaam loses his Immune."""

    TARGET = ActionArg()

    def do(self, source, target):
        charge = getattr(target, "staff_charge", 0) + 1
        if charge <= 3:
            target.staff_charge = charge
            target.staff_fired = False
            return
        target.staff_charge = 0
        target.staff_fired = True
        heroic = target.id.endswith("H")
        bosses = RandomID(*(id + ("H" if heroic else "") for id in RAFAAM_BOSSES))
        return source.game.queue_actions(source, [Summon(CONTROLLER, bosses)])


class StaffCharging(Evaluator):
    def check(self, source):
        return not getattr(source, "staff_fired", False)


class LOEA16_2:
    """Staff of Origination"""

    update = StaffCharging() & Refresh(FRIENDLY_HERO, {GameTag.CANT_BE_DAMAGED: True})
    events = OWN_TURN_BEGIN.on(StaffOfOrigination(SELF))


class LOEA16_2H:
    """Staff of Origination (Heroic)"""

    update = StaffCharging() & Refresh(FRIENDLY_HERO, {GameTag.CANT_BE_DAMAGED: True})
    events = OWN_TURN_BEGIN.on(StaffOfOrigination(SELF))


class Rummage(TargetedAction):
    """
    Rummage (the wiki): "Once the player has used Rummage to receive each of
    the special cards listed below, using the Hero Power will instead
    generate a Boom Bot each time." Each artifact is found once.
    """

    TARGET = ActionArg()
    ARTIFACTS = (
        "LOEA16_6", "LOEA16_7", "LOEA16_8", "LOEA16_9", "LOEA16_10",
        "LOEA16_11", "LOEA16_12", "LOEA16_13", "LOEA16_14", "LOEA16_15",
    )

    def do(self, source, target):
        found = getattr(target, "artifacts_found", ())
        left = [id for id in self.ARTIFACTS if id not in found]
        if not left:
            return source.game.queue_actions(source, [Give(target, "GVG_110t")])
        artifact = source.game.random.choice(left)
        target.artifacts_found = tuple(found) + (artifact,)
        return source.game.queue_actions(source, [Give(target, artifact)])


class LOEA16_16:
    """Rummage"""

    activate = Rummage(CONTROLLER)


class LOEA16_16H:
    """Rummage (Heroic)"""

    activate = Rummage(CONTROLLER)


class LOEA16_13:
    """Eye of Orsis"""

    # "Discover a minion and gain 3 copies of it."
    play = Discover(CONTROLLER, RandomMinion()).then(
        Give(CONTROLLER, Discover.CARD), Give(CONTROLLER, Copy(Discover.CARD)) * 2
    )


class LOEA16_25:
    """Lady Naz'jar"""

    # "At the end of your turn, replace all other minions with new ones of
    # the same Cost."
    events = OWN_TURN_END.on(Evolve(ALL_MINIONS - SELF, 0))


class LOEA16_25H:
    """Lady Naz'jar (Heroic)"""

    events = OWN_TURN_END.on(Evolve(ALL_MINIONS - SELF, 0))


class LOEA16_6:
    """Shard of Sulfuras"""

    play = Hit(ALL_CHARACTERS, 5)


class LOEA16_7:
    """Benediction Splinter"""

    play = Heal(ALL_CHARACTERS, 10)


class LOEA16_8:
    """Putress' Vial"""

    play = Destroy(RANDOM_ENEMY_MINION)


# Putressed (Unused)
LOEA16_8a = AttackHealthSwapBuff()


class LOEA16_9:
    """Lothar's Left Greave"""

    play = Hit(ENEMY_CHARACTERS, 3)


class LOEA16_10:
    """Hakkari Blood Goblet"""

    requirements = {PlayReq.REQ_MINION_TARGET: 0, PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Morph(TARGET, "LOE_010")


class LOEA16_11:
    """Crown of Kael'thas"""

    play = Hit(RANDOM_CHARACTER, 1) * 10


class LOEA16_12:
    """Medivh's Locket"""

    play = Morph(FRIENDLY_HAND, "GVG_003")


class LOEA16_14:
    """Khadgar's Pipe"""

    play = (
        Give(OPPONENT, RandomSpell()),
        Give(PLAYER, RandomSpell()).then(Buff(Give.CARD, "GBL_008e")),
    )


class LOEA16_15:
    """Ysera's Tear"""

    play = ManaThisTurn(CONTROLLER, 4)


class LOEA16_18:
    """Zinaar"""

    events = OWN_TURN_END.on(Give(CONTROLLER, RandomWish))


class LOEA16_18H:
    """Zinaar (Heroic)"""

    events = OWN_TURN_END.on(Give(CONTROLLER, RandomWish))


class LOEA16_19:
    """Sun Raider Phaerix"""

    events = OWN_TURN_END.on(Give(CONTROLLER, "LOEA16_20"))


class LOEA16_19H:
    """Sun Raider Phaerix (Heroic)"""

    update = Refresh(FRIENDLY_MINIONS - SELF, {GameTag.CANT_BE_DAMAGED: True})


LOEA16_20H = buff(immune=True)


class LOEA16_21:
    """Chieftain Scarvash"""

    update = Refresh(ENEMY_HAND, {GameTag.COST: +1})


class LOEA16_21H:
    """Chieftain Scarvash (Heroic)"""

    update = Refresh(ENEMY_HAND, {GameTag.COST: +2})


class LOEA16_22:
    """Archaedas"""

    events = OWN_TURN_END.on(Morph(RANDOM_ENEMY_MINION, "LOEA06_02t"))


class LOEA16_22H:
    """Archaedas (Heroic)"""

    events = OWN_TURN_END.on(Morph(RANDOM_ENEMY_MINION, "LOEA06_02t"))


class LOEA16_23:
    """Lord Slitherspear"""

    events = OWN_TURN_END.on(Summon(CONTROLLER, "LOEA09_5") * Count(ENEMY_MINIONS))


class LOEA16_23H:
    """Lord Slitherspear (Heroic)"""

    events = OWN_TURN_END.on(Summon(CONTROLLER, "LOEA09_5") * Count(ENEMY_MINIONS))


class LOEA16_24:
    """Giantfin"""

    events = OWN_TURN_END.on(DrawUntil(CONTROLLER, Count(ENEMY_HAND)))


class LOEA16_24H:
    """Giantfin (Heroic)"""

    events = OWN_TURN_END.on(Draw(CONTROLLER) * 2)


class LOEA16_26:
    """Skelesaurus Hex"""

    events = OWN_TURN_END.on(
        Give(ALL_PLAYERS, RandomCollectible()).then(Buff(Give.CARD, "LOEA13_2e"))
    )


class LOEA16_26H:
    """Skelesaurus Hex (Heroic)"""

    events = OWN_TURN_END.on(
        Give(CONTROLLER, RandomCollectible()).then(Buff(Give.CARD, "LOEA13_2e"))
    )


class LOEA16_27:
    """The Steel Sentinel"""

    tags = {GameTag.HEAVILY_ARMORED: True}


class LOEA16_27H:
    """The Steel Sentinel (Heroic)"""

    tags = {GameTag.HEAVILY_ARMORED: True}


class LOEA16_20:
    """Blessing of the Sun"""

    requirements = {
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }
    play = Buff(TARGET, "LOEA16_20e")


LOEA16_20e = buff(immune=True)


##
# Misc.


class LOE_008:
    """Eye of Hakkar (Unused)"""

    requirements = {PlayReq.REQ_MINION_TARGET: 0}
    play = Summon(CONTROLLER, RANDOM(ENEMY_DECK + SECRET))


class LOE_008H:
    """Eye of Hakkar (Unused) (Heroic)"""

    play = Summon(CONTROLLER, RANDOM(ENEMY_DECK + SECRET))


class LOEA_01:
    """Looming Presence"""

    play = Draw(CONTROLLER) * 2, GainArmor(FRIENDLY_HERO, 4)


class LOEA_01H:
    """Looming Presence (Heroic)"""

    play = Draw(CONTROLLER) * 3, GainArmor(FRIENDLY_HERO, 6)


class LOEA15_3:
    """Boneraptor (Unused)"""

    play = Steal(ENEMY_WEAPON)


class LOEA15_3H:
    """Boneraptor (Unused) (Heroic)"""

    play = Steal(ENEMY_WEAPON)
