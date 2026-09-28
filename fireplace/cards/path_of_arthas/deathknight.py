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


