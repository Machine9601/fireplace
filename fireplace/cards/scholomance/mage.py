from hearthstone.enums import Zone

from ..utils import *


def _flatten(result):
    """The cards in what queue_actions returns (lists of lists)."""
    if isinstance(result, (list, tuple)):
        return [card for item in result for card in _flatten(item)]
    return [] if result is None else [result]


class JandiceBarovSummon(TargetedAction):
    """
    Jandice Barov: summon two random 5-Cost minions, then its player secretly
    picks one of them, which dies when it takes damage (SCH_351e).
    """

    TARGET = ActionArg()

    def do(self, source, target):
        summoned = []
        for _ in range(2):
            card_set = RandomMinion(cost=5).find_cards(source)
            if not card_set:
                continue
            card = source.game.random.choice(card_set)
            result = source.game.queue_actions(source, [Summon(target, card)])
            summoned += [c for c in _flatten(result) if c.zone == Zone.PLAY]
        if summoned:
            source.game.queue_actions(
                source,
                [Choice(target, summoned).then(Buff(Choice.CARD, "SCH_351e"))],
            )


class CombustionHit(TargetedAction):
    """
    Combustion: $4 damage to a minion; any excess damages both of its
    neighbours.
    """

    TARGET = ActionArg()

    def do(self, source, target):
        neighbours = list(target.adjacent_minions)
        # The card is IMMUNE_TO_SPELLPOWER in CardDefs.xml: its script adds
        # the Spell Damage to the $4 itself, once.
        amount = source.controller.get_spell_damage(source, 4)
        excess = max(0, amount - target.health)
        source.game.queue_actions(source, [Predamage(target, amount)])
        if excess:
            for minion in neighbours:
                source.game.queue_actions(source, [Predamage(minion, excess)])


##
# Minions


class SCH_241:
    """Firebrand"""

    # <b><b>Spellburst</b>:</b> Deal 4 damage randomly split among all_enemy
    # minions.
    spellburst = Hit(RANDOM_ENEMY_MINION, 1) * 4


class SCH_243:
    """Wyrm Weaver"""

    # <b>Spellburst:</b> Summon two 1/3 Mana Wyrms.
    spellburst = SummonBothSides(CONTROLLER, "NEW1_012") * 2


class SCH_350:
    """Wand Thief"""

    # <b>Combo:</b> <b>Discover</b> a Mage_spell.
    combo = DISCOVER(RandomSpell(card_class=CardClass.MAGE))


class SCH_351:
    """Jandice Barov"""

    # [x]<b>Battlecry:</b> Summon two random 5-Cost minions. Secretly pick one
    # that dies _when it takes damage.

    # The choice is between the two minions summoned (the old script offered
    # two unevaluated tag readings and never marked a summoned minion).
    play = JandiceBarovSummon(CONTROLLER)


class SCH_351e:
    events = Damage(OWNER).on(Destroy(OWNER))


class SCH_352:
    """Potion of Illusion"""

    # Add 1/1 copies of your minions to your hand. They cost (1).
    play = Give(
        CONTROLLER, MultiBuff(Copy(FRIENDLY_MINIONS), ["SCH_352e", "SCH_352e2"])
    )


class SCH_352e:
    atk = SET(1)
    max_health = SET(1)


class SCH_352e2:
    cost = SET(1)
    events = REMOVED_IN_PLAY


class SCH_400:
    """Mozaki, Master Duelist"""

    # After you cast a spell, gain <b>Spell Damage +1</b>.
    events = Play(CONTROLLER, SPELL).after(Buff(SELF, "SCH_400e2"))


class SCH_400e2:
    tags = {GameTag.SPELLPOWER: 1}


##
# Spells


class SCH_348:
    """Combustion"""

    # [x]Deal $4 damage to a minion. Any excess damages both neighbors.
    requirements = {
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }
    # The excess is what the target cannot take (its Health before the hit),
    # dealt to both neighbours it had; Spell Damage counts once, on the $4.
    play = CombustionHit(TARGET)


class SCH_353:
    """Cram Session"""

    # Draw $1 |4(card, cards) <i>(improved by <b>Spell Damage</b>)</i>.
    play = Draw(CONTROLLER) * SPELL_DAMAGE(1)


class SCH_509:
    """Brain Freeze"""

    # <b>Freeze</b> a minion. <b>Combo:</b> Also deal $3 damage to it.
    requirements = {
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }
    play = Freeze(TARGET)
    combo = Freeze(TARGET), Hit(TARGET, 3)
