from ..utils import *

##
# Minions


SPELLS_OF_5_OR_MORE_CAST_THIS_TURN = FuncSelector(
    lambda entities, source: [
        card
        for card in source.controller.cards_played_this_game
        if card.type == CardType.SPELL
        and card.turn_played == source.game.turn
        and not card.cant_play
        and card.cost >= 5
    ]
)


class LOOT_130:
    """Arcane Tyrant"""

    # Costs (0) if you've cast a spell that costs (5) or more this turn.
    # A condition, not a trigger: a Tyrant that comes to the hand after the
    # spell costs (0) too (WP-185).
    class Hand:
        update = Find(SPELLS_OF_5_OR_MORE_CAST_THIS_TURN) & Refresh(
            SELF, {GameTag.COST: SET(0)}
        )


# No longer used (WP-185), kept: the database counts the cards the modules add
# (the server's health check reads that count, D-40).
@custom_card
class LOOT_130e:
    tags = {
        GameTag.CARDNAME: "Arcane Tyrant Buff",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.TAG_ONE_TURN_EFFECT: True,
    }
    cost = SET(0)
    events = REMOVED_IN_PLAY


class LOOT_149:
    """Corridor Creeper"""

    # Costs (1) less whenever a minion dies while this is_in_your hand.
    class Hand:
        events = Death(MINION).on(Buff(SELF, "LOOT_149e"))


class LOOT_149e:
    events = REMOVED_IN_PLAY
    tags = {GameTag.COST: -1}


class LOOT_161:
    """Carnivorous Cube"""

    # <b>Battlecry:</b> Destroy a friendly minion. <b>Deathrattle:</b> Summon 2 copies of
    # it.
    requirements = {
        PlayReq.REQ_TARGET_IF_AVAILABLE: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
    }
    play = Destroy(TARGET)
    deathrattle = HAS_TARGET & Summon(CONTROLLER, Copy(TARGET)) * 2


class LOOT_193:
    """Shimmering Courser"""

    # Only you can target this with spells and Hero Powers.
    update = CurrentPlayer(OPPONENT) & Refresh(
        SELF,
        {
            GameTag.CANT_BE_TARGETED_BY_HERO_POWERS: True,
            GameTag.CANT_BE_TARGETED_BY_ABILITIES: True,
        },
    )


class LOOT_389:
    """Rummaging Kobold"""

    # <b>Battlecry:</b> Return one of your destroyed weapons to your hand.
    play = Give(CONTROLLER, Copy(RANDOM(FRIENDLY + KILLED + WEAPON)))


class LOOT_414:
    """Grand Archivist"""

    # At the end of your turn, cast a spell from your deck <i>(targets chosen
    # randomly)</i>.
    events = OWN_TURN_END.on(CastSpell(RANDOM(FRIENDLY_DECK + SPELL)))


class LOOT_529:
    """Void Ripper"""

    # <b>Battlecry:</b> Swap the Attack and Health of all_other_minions.
    # "all other minions": not itself (WP-185).
    play = Buff(ALL_MINIONS - SELF, "LOOT_529e")


LOOT_529e = AttackHealthSwapBuff()


class LOOT_539:
    """Spiteful Summoner"""

    # [x]<b>Battlecry:</b> Reveal a spell from your deck. Summon a random minion with the
    # same Cost.
    play = Reveal(RANDOM(FRIENDLY_DECK + SPELL)).then(
        Summon(CONTROLLER, RandomMinion(cost=COST(Reveal.TARGET)))
    )


class LOOT_540:
    """Dragonhatcher"""

    # At the end of your turn, <b>Recruit</b> a Dragon.
    events = OWN_TURN_END.on(Recruit(DRAGON))
