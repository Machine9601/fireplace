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


