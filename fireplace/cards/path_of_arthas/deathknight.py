"""Path of Arthas: the 26 death knight cards of its initiation set (texts of
HearthstoneJSON build 253216, the one the official wiki shows)."""

from hearthstone.enums import Zone

from ... import enums
from ...dsl.selector import Selector
from ..utils import *


# --- RLK_042
class RLK_042:
    """Horn of Winter"""

    # Refresh 2 Mana Crystals.
    play = FillMana(CONTROLLER, 2)


# --- RLK_038
class RLK_038:
    """Icy Touch"""

    # Deal $2 damage to an enemy and <b>Freeze</b> it.
    requirements = {PlayReq.REQ_ENEMY_TARGET: 0, PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Hit(TARGET, 2), Freeze(TARGET)


# --- RLK_110
class RLK_110:
    """Ymirjar Frostbreaker"""

    # <b>Battlecry:</b> Gain +1 Attack for each Frost spell in your hand.
    play = Buff(SELF, "RLK_110e") * Count(FRIENDLY_HAND + FROST + SPELL)


RLK_110e = buff(atk=1)


# --- RLK_516
class RLK_516:
    """Bone Breaker"""

    # After your hero attacks a minion, deal 2 damage to the enemy hero.
    events = Attack(FRIENDLY_HERO, ALL_MINIONS).after(Hit(ENEMY_HERO, 2))


# --- RLK_018
class RLK_018:
    """Plague Strike"""

    # Deal $3 damage to a minion. If it dies, summon a 2/2 Zombie with
    # <b>Rush</b>. (The wiki: it checks whether the minion was dealt lethal
    # damage.)
    requirements = {PlayReq.REQ_MINION_TARGET: 0, PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Hit(TARGET, 3), Dead(TARGET) & Summon(CONTROLLER, "RLK_018t")


# --- RLK_056
class UnholyFrenzyAttack(TargetedAction):
    """Your minions attack TARGET, left to right, while it lives; then
    resummon (a new copy of) any of them that died."""

    TARGET = ActionArg()

    def do(self, source, target):
        game = source.game
        died = []
        for minion in list(source.controller.field):
            if target.dead or target.zone != Zone.PLAY:
                break
            if minion.dead or minion.zone != Zone.PLAY or minion.dormant:
                continue
            game.queue_actions(source, [Attack(minion, target)])
            if minion.dead:
                died.append(minion.id)
        if died:
            game.queue_actions(source, [Deaths()])
            for id in died:
                game.queue_actions(source, [Summon(CONTROLLER, id)])


class RLK_056:
    """Unholy Frenzy"""

    # Choose an enemy minion. Your minions attack it. Resummon any that die.
    requirements = {
        PlayReq.REQ_ENEMY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }
    play = UnholyFrenzyAttack(TARGET)


