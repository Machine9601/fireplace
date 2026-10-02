from ..utils import *


# A spell its controller played this turn that costs (5) or more: the cost is
# read only on such a spell (`COST >= 5` on every entity read the Defender's
# own cost, an endless recursion).
def _big_spell_cast_this_turn(entities, source):
    return [
        e
        for e in entities
        if getattr(e, "played_this_turn", False)
        and e.type == CardType.SPELL
        and e.controller == source.controller
        and e.cost >= 5
    ]


BIG_SPELL_CAST_THIS_TURN = FuncSelector(_big_spell_cast_this_turn)

##
# Minions


class ULD_133:
    """Crystal Merchant"""

    # If you have any unspent Mana at the end of your turn, draw a card.
    # MANA is the crystals (RESOURCES), CURRENT_MANA what is left (WP-190).
    events = OWN_TURN_END.on((CURRENT_MANA(CONTROLLER) > 0) & Draw(CONTROLLER))


class ULD_137:
    """Garden Gnome"""

    # [x]<b>Battlecry:</b> If you're holding a spell that costs (5) or more, summon two 2/2
    # Treants.
    powered_up = Find(FRIENDLY_HAND + SPELL + (COST >= 5))
    play = powered_up & SummonBothSides(CONTROLLER, "ULD_137t") * 2


class ULD_138:
    """Anubisath Defender"""

    # <b>Taunt</b>. Costs (0) if you've cast a spell that costs (5) or more this turn.
    # A condition of the turn, not a buff: a Defender drawn after the spell
    # costs 0 too, and none costs 0 any more the next turn (the buff stayed)
    # (WP-190).
    cost_mod = Find(BIG_SPELL_CAST_THIS_TURN) & -100


class ULD_139:
    """Elise the Enlightened"""

    # <b>Battlecry:</b> If your deck has no duplicates, duplicate your hand.
    powered_up = -FindDuplicates(FRIENDLY_DECK)
    play = powered_up & Give(CONTROLLER, ExactCopy(FRIENDLY_HAND))


class ULD_292:
    """Oasis Surger"""

    # <b>Rush</b> <b>Choose One -</b> Gain +2/+2; or Summon a copy of this minion.
    choose = ("ULD_292a", "ULD_292b")
    play = ChooseBoth(CONTROLLER) & (
        Buff(SELF, "ULD_292ae"),
        Summon(CONTROLLER, ExactCopy(SELF)),
    )


class ULD_292a:
    play = Buff(SELF, "ULD_292ae")


# CardDefs gives "Focused" no stats: +2/+2 never came (WP-190).
ULD_292ae = buff(+2, +2)


class ULD_292b:
    requirements = {
        PlayReq.REQ_NUM_MINION_SLOTS: 2,
    }
    play = Summon(CONTROLLER, ExactCopy(SELF))


##
# Spells


class ULD_131:
    """Untapped Potential"""

    # [x]<b>Quest:</b> End 4 turns with any unspent Mana. <b>Reward:</b> Ossirian Tear.
    progress_total = 4
    quest = OWN_TURN_END.on((CURRENT_MANA(CONTROLLER) > 0) & AddProgress(SELF, SELF))
    reward = Summon(CONTROLLER, "ULD_131p")


class ULD_131p:
    """Ossirian Tear"""

    # <b>Passive Hero Power</b> Your <b>Choose One</b> cards have both effects combined.
    tags = {enums.PASSIVE_HERO_POWER: True}
    update = Refresh(CONTROLLER, {GameTag.CHOOSE_BOTH: True})


class ULD_134:
    """BEEEES!!!"""

    # [x]Choose a minion. Summon four 1/1 Bees that attack it.
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_NUM_MINION_SLOTS: 1,
    }
    play = (
        Summon(CONTROLLER, "ULD_134t").then(Dead(TARGET) | Attack(Summon.CARD, TARGET))
        * 4
    )


class ULD_135:
    """Hidden Oasis"""

    # <b>Choose One</b> - Summon a 6/6 Ancient with <b>Taunt</b>; or Restore #12 Health.
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }
    choose = ("ULD_135a", "ULD_135b")
    play = ChooseBoth(CONTROLLER) & (Summon(CONTROLLER, "ULD_135at"), Heal(TARGET, 12))


class ULD_135a:
    requirements = {
        PlayReq.REQ_NUM_MINION_SLOTS: 1,
    }
    play = Summon(CONTROLLER, "ULD_135at")


class ULD_135b:
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }
    play = Heal(TARGET, 12)


class ULD_136:
    """Worthy Expedition"""

    # <b>Discover</b> a <b>Choose One</b> card.
    play = DISCOVER(RandomCollectible(choose_one=True, card_class=CardClass.DRUID))


class ULD_273:
    """Overflow"""

    # Restore #5 Health to all characters. Draw 5 cards.
    play = Heal(ALL_CHARACTERS, 5), Draw(CONTROLLER) * 5
