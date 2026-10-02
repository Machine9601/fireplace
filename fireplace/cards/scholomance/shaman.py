from ..utils import *


# Instructor Fireheart: discover a spell that costs (1) or more; if it is
# played this turn, discover again.
FIREHEART_DISCOVER = Discover(CONTROLLER, RandomSpell(cost=range(1, 100))).then(
    Give(CONTROLLER, Discover.CARD),
    StoringBuff(CONTROLLER, "SCH_507e", Discover.CARD),
)

##
# Minions


class SCH_236:
    """Diligent Notetaker"""

    # <b>Spellburst:</b> Return the spell to your hand.
    # The spell itself, from its player's graveyard, not the Notetaker
    spellburst = Give(CONTROLLER, Spellburst.SPELL)


class SCH_507:
    """Instructor Fireheart"""

    # [x]<b>Battlecry:</b> <b>Discover</b> a spell that costs (1) or more. If
    # you play it this turn, repeat this effect.
    # The enchantment that waits for the spell is its player's (an enchantment
    # on the spell is gone once the spell is played, and never heard it); it
    # remembers the spell, and lasts this turn (TAG_ONE_TURN_EFFECT).
    play = FIREHEART_DISCOVER


class SCH_507e:
    events = Play(CONTROLLER, STORE_CARD).after(Destroy(SELF), FIREHEART_DISCOVER)


class SCH_537:
    """Trick Totem"""

    # At the end of your turn, cast a random spell that costs (3) or less.
    events = OWN_TURN_END.on(CastSpell(RandomSpell(cost=range(0, 4))))


class SCH_615:
    """Totem Goliath"""

    # <b>Deathrattle:</b> Summon all four basic Totems. <b>Overload: (1)</b>
    # The Overload (1) of its text, which CardDefs.xml (patch 21.8) lacks
    tags = {GameTag.OVERLOAD: 1}
    deathrattle = Summon(CONTROLLER, BASIC_TOTEMS)


##
# Spells


class SCH_235:
    """Devolving Missiles"""

    # [x]Shoot three missiles at random enemy minions that transform them into
    # ones that cost (1) less.
    play = Evolve(RANDOM_ENEMY_MINION, -1) * 3


class SCH_270:
    """Primordial Studies"""

    # <b>Discover</b> a <b>Spell Damage</b> minion. Your next one costs (1)
    # less.
    # The reduction first: an action after a choice in the same tuple is lost
    # (annex A47 of the rules); the minion discovered then gets it.
    play = Buff(CONTROLLER, "SCH_270e"), DISCOVER(RandomMinion(spell_damage=True))


class SCH_270e:
    update = Refresh(FRIENDLY_HAND + SPELLPOWER + MINION, buff="SCH_270e2")
    events = Play(CONTROLLER, SPELLPOWER + MINION).after(Destroy(SELF))


class SCH_270e2:
    events = REMOVED_IN_PLAY
    tags = {GameTag.COST: -1}


class SCH_271:
    """Molten Blast"""

    # Deal $2 damage. Summon that many 1/1 Elementals.
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }
    play = (Hit(TARGET, 2), Summon(CONTROLLER, "CS2_050") * SPELL_DAMAGE(2))


class SCH_273:
    """Ras Frostwhisper"""

    # At the end of your turn, deal $1 damage to all enemies <i>(improved by
    # <b>Spell Damage</b>)</i>.
    # All enemies: the enemy hero too
    events = OWN_TURN_END.on(Hit(ENEMY_CHARACTERS, SPELL_DAMAGE(1)))


class SCH_535:
    """Tidal Wave"""

    # <b>Lifesteal</b> Deal $3 damage to all minions.
    play = Hit(ALL_MINIONS, 3)


##
# Weapons


class SCH_301:
    """Rune Dagger"""

    # After your hero attacks, gain <b>Spell Damage +1</b> this turn.
    # The Spell Damage is its player's (a weapon's own SPELLPOWER is not
    # counted by Player.spellpower), for this turn (TAG_ONE_TURN_EFFECT)
    events = Attack(FRIENDLY_HERO).after(Buff(CONTROLLER, "SCH_301e"))


class SCH_301e:
    # A player's Spell Damage is read from auras (as Arcane Power, KARA_00_06e)
    update = Refresh(CONTROLLER, {GameTag.SPELLPOWER: +1})
