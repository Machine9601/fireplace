from hearthstone.enums import Zone

from ..utils import *


class FriendlyMinionsAttackToo(TargetedAction):
    """
    Trueaim Crescent: after the hero attacks a minion, every friendly minion
    attacks it too, in the order they came into play, until it is destroyed.
    """

    TARGET = ActionArg()

    def do(self, source, target):
        player = source.controller
        for minion in sorted(player.field, key=lambda m: m.play_counter):
            if target.dead or target.zone != Zone.PLAY:
                break
            if minion.dead or minion.zone != Zone.PLAY:
                continue
            source.game.queue_actions(source, [Attack(minion, target)])


##
# Minions


class SCH_276:
    """Magehunter"""

    # <b>Rush</b> Whenever this attacks a minion, <b>Silence</b> it.
    events = Attack(SELF, MINION).on(Silence(Attack.DEFENDER))


class SCH_354:
    """Ancient Void Hound"""

    # [x]At the end of your turn, steal 1 Attack and Health from all enemy
    # minions.
    # Every enemy minion loses 1 Attack and 1 Health (its Attack never below
    # 0), and the Hound gains +1/+1 for each one affected (hearthstone.wiki.gg):
    # a 0-Attack minion is drained too.
    events = OWN_TURN_END.on(
        Buff(ENEMY_MINIONS, "SCH_354e").then(Buff(SELF, "SCH_354e2"))
    )


SCH_354e = buff(-1, -1)
SCH_354e2 = buff(+1, +1)
SCH_354e2a = buff(atk=+1)
SCH_354e2b = buff(health=+1)
SCH_354ea = buff(atk=-1)
SCH_354eb = buff(health=-1)


class SCH_355:
    """Shardshatter Mystic"""

    # <b>Battlecry:</b> Destroy a Soul Fragment in your deck to deal 3 damage
    # to all other minions.
    powered_up = Find(FRIENDLY_DECK + ID(SOUL_FRAGMENT))
    play = powered_up & (
        Destroy(RANDOM(FRIENDLY_DECK + ID(SOUL_FRAGMENT))),
        Hit(ALL_MINIONS - SELF, 3),
    )


class SCH_538:
    """Ace Hunter Kreen"""

    # Your other characters are <b>Immune</b> while attacking.
    update = Refresh(FRIENDLY_CHARACTERS - SELF, {GameTag.IMMUNE_WHILE_ATTACKING: True})


class SCH_603:
    """Star Student Stelina"""

    # [x]<b>Outcast:</b> Look at 3 cards in your opponent's hand. Shuffle one
    # of them into their deck.
    outcast = Choice(CONTROLLER, RANDOM(ENEMY_HAND, 3)).then(
        Shuffle(OPPONENT, Choice.CARD)
    )


class SCH_618:
    """Blood Herald"""

    # Whenever a friendly minion dies while this is in your hand, gain +1/+1.
    # (`Hand`, not `Hands`; Death(FRIENDLY_MINIONS) only reads minions in play.)
    class Hand:
        events = Death(FRIENDLY + MINION).on(Buff(SELF, "SCH_618e"))


SCH_618e = buff(+1, +1)


class SCH_704:
    """Soulshard Lapidary"""

    # [x]<b>Battlecry:</b> Destroy a Soul Fragment in your deck to give your
    # hero +5 Attack this turn.
    powered_up = Find(FRIENDLY_DECK + ID(SOUL_FRAGMENT))
    play = powered_up & (
        Destroy(RANDOM(FRIENDLY_DECK + ID(SOUL_FRAGMENT))),
        Buff(FRIENDLY_HERO, "SCH_704e"),
    )


SCH_704e = buff(atk=5)


class SCH_705:
    """Vilefiend Trainer"""

    # <b>Outcast:</b> Summon two 1/1_Demons.
    outcast = SummonBothSides(CONTROLLER, "SCH_705t") * 2


##
# Spells


class SCH_253:
    """Cycle of Hatred"""

    # Deal $3 damage to all minions. Summon a 3/3 Spirit for every minion
    # killed.
    play = Hit(ALL_MINIONS, 3), Summon(CONTROLLER, "SCH_253t") * Count(
        ALL_MINIONS + DEAD
    )


class SCH_356:
    """Glide"""

    # [x]Shuffle your hand into your deck. Draw 4 cards. <b>Outcast:</b> Your
    # opponent does the same.
    play = Shuffle(CONTROLLER, FRIENDLY_HAND), (Draw(CONTROLLER) * 4)
    outcast = (
        Shuffle(CONTROLLER, FRIENDLY_HAND),
        Shuffle(OPPONENT, ENEMY_HAND),
        (Draw(CONTROLLER) * 4),
        (Draw(OPPONENT) * 4),
    )


class SCH_357:
    """Fel Guardians"""

    # Summon three 1/2 Demons with <b>Taunt</b>. Costs (1) less whenever
    # a_friendly minion dies.
    # Only the deaths while it is in its player's hand (an in-hand effect), not
    # every friendly minion killed in the game.
    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    play = Summon(CONTROLLER, "SCH_357t") * 3

    class Hand:
        events = Death(FRIENDLY + MINION).on(Buff(SELF, "SCH_357e"))


class SCH_357e:
    tags = {GameTag.COST: -1}
    events = REMOVED_IN_PLAY


class SCH_422:
    """Double Jump"""

    # Draw an <b>Outcast</b> card from your deck.
    play = ForceDraw(RANDOM(FRIENDLY_DECK + OUTCAST))


class SCH_600:
    """Demon Companion"""

    # Summon a random Demon Companion.
    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    entourage = ["SCH_600t1", "SCH_600t2", "SCH_600t3"]
    play = Summon(CONTROLLER, RandomEntourage())


class SCH_600t3:
    """Kolek"""

    # Your other minions have +1 Attack.
    update = Refresh(FRIENDLY_MINIONS - SELF, buff="SCH_600t3e")


SCH_600t3e = buff(atk=1)


##
# Weapons


class SCH_252:
    """Marrowslicer"""

    # <b>Battlecry:</b> Shuffle 2 Soul Fragments into your deck.
    play = Shuffle(CONTROLLER, SOUL_FRAGMENT) * 2


class SCH_279:
    """Trueaim Crescent"""

    # After your Hero attacks a minion, your minions attack it too.
    # Each friendly minion, in the order they came into play, attacks it in
    # turn, until it is destroyed; these attacks use none of the minions' own.
    events = Attack(FRIENDLY_HERO, ALL_MINIONS).after(
        FriendlyMinionsAttackToo(Attack.DEFENDER)
    )
