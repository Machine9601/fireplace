from ..utils import *

##
# Minions


class SCH_317:
    """Playmaker"""

    # [x]After you play a <b>Rush</b> minion, summon a copy _with 1 Health
    # remaining.
    events = Play(CONTROLLER, RUSH + MINION).after(
        Summon(CONTROLLER, ExactCopy(Play.CARD)).then(SetCurrentHealth(Summon.CARD, 1))
    )


class SCH_337:
    """Troublemaker"""

    # At the end of your turn, summon two 3/3 Ruffians that attack random
    # enemies.
    events = OWN_TURN_END.on(
        SummonBothSides(CONTROLLER, "SCH_337t").then(
            Attack(Summon.CARD, RANDOM(ENEMY_CHARACTERS))
        )
        * 2
    )


class SCH_621:
    """Rattlegore"""

    # <b>Deathrattle:</b> Resummon this with -1/-1.
    # One Rattlegore, with 1 less Attack and Health than the one that died
    # (the old script also summoned an exact copy at full stats)
    deathrattle = SummonCustomMinion(
        CONTROLLER, "SCH_621", 9, ATK(SELF) - 1, MAX_HEALTH(SELF) - 1
    )


##
# Spells


class SCH_237:
    """Athletic Studies"""

    # <b>Discover</b> a <b>Rush</b> minion. Your next one costs (1) less.
    # The reduction first: an action after a choice in the same tuple is lost
    # (annex A47 of the rules); the minion discovered then gets it.
    play = Buff(CONTROLLER, "SCH_237e"), DISCOVER(RandomMinion(rush=True))


class SCH_237e:
    update = Refresh(FRIENDLY_HAND + RUSH + MINION, buff="SCH_237e2")
    events = Play(CONTROLLER, RUSH + MINION).after(Destroy(SELF))


class SCH_237e2:
    events = REMOVED_IN_PLAY
    tags = {GameTag.COST: -1}


class SCH_525:
    """In Formation!"""

    # Add 2 random <b>Taunt</b> minions to your hand.
    play = Give(CONTROLLER, RandomMinion(taunt=True)) * 2


##
# Weapons


class SCH_238:
    """Reaper's Scythe"""

    # [x]<b>Spellburst</b>: Also damages adjacent minions this turn.
    # The enchantment goes on the hero (the events of a weapon's enchantment
    # are never heard), for this turn (TAG_ONE_TURN_EFFECT), and acts while the
    # Scythe is equipped.
    spellburst = Buff(FRIENDLY_HERO, "SCH_238e")


class SCH_238e:
    events = Attack(OWNER).on(
        Find(FRIENDLY_WEAPON + ID("SCH_238"))
        & Hit(ADJACENT(Attack.DEFENDER), ATK(OWNER))
    )
