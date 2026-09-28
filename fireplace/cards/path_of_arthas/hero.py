"""The death knight's base Hero Power and its upgrade (Justicar Trueheart)."""

from ..utils import *


class HERO_11bp:
    """Ghoul Charge"""

    # [x]<b>Hero Power</b> Summon a 1/1 Ghoul with <b>Charge</b>. It dies at
    # end of turn.
    activate = Summon(CONTROLLER, "HERO_11bpt")


class HERO_11bpt:
    """Frail Ghoul"""

    # [x]<b>Charge</b> At the end of your turn, this minion dies.
    # Summoned on the opponent's turn, it lives until the end of its owner's
    # turn (the wiki, Ghoul Charge).
    events = OWN_TURN_END.on(Destroy(SELF))


class HERO_11bp2:
    """Ghoul Frenzy"""

    # [x]<b>Hero Power</b> Summon a 2/1 Ghoul with <b>Charge</b>. It dies at
    # end of turn.
    activate = Summon(CONTROLLER, "HERO_11bp2t")


class HERO_11bp2t:
    """Frenzied Ghoul"""

    # [x]<b>Charge</b> At the end of your turn, this minion dies.
    events = OWN_TURN_END.on(Destroy(SELF))
