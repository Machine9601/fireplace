"""
Decks Assemble
"""

from ..utils import *


class TB_010:
    """Deckbuilding Enchant

    The start of the turn Discovers a card (the draw is DecksAssembleBrawl's to
    replace), a card played, once its Battlecry has resolved, shuffles a copy
    into the deck (The Coin excepted). The hand going back into the deck at the
    end of the turn is DecksAssembleBrawl's: it comes before the "end of turn"
    effects.
    """

    events = (
        OWN_TURN_BEGIN.on(DISCOVER(RandomCollectible())),
        Play(CONTROLLER, -ID("GAME_005")).after(Shuffle(CONTROLLER, Copy(Play.CARD))),
    )


class TB_011:
    """Tarnished Coin"""

    play = ManaThisTurn(CONTROLLER, 1)
