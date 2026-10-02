from ..utils import *


class DiscoverOnly(GenericChoice):
    """
    "Discover … Summon it" (Revive Pet, Beaststalker Tavish, Tamsin's
    Phylactery): the chosen card is not added to the hand (GenericChoice puts it
    there after the callbacks, and takes a summoned minion or a cast secret
    back); the others are put aside.
    """

    def choose(self, card):
        Choice.choose(self, card)
        for _card in self.cards:
            if _card != card:
                _card.discard()


class SecretsToDiscover(LazyValue):
    """
    Three of the source's entourage of Secrets, none of them already in play
    (a Secret in play cannot be cast again); read when the choice opens.
    """

    def evaluate(self, source):
        controller = source.controller
        active = [secret.id for secret in controller.secrets]
        pool = [id for id in source.entourage if id not in active]
        picked = source.game.random.sample(pool, min(3, len(pool)))
        return [controller.card(id, source) for id in picked]


class GiveDeathrattleOf(TargetedAction):
    """
    Give the target minions the Deathrattles of a card (Tamsin's Phylactery).
    CopyDeathrattleBuff copies them to the source.
    """

    TARGET = ActionArg()
    CARD = ActionArg()

    def do(self, source, target, card):
        if isinstance(card, list):
            card = card[0]
        if not card.has_deathrattle:
            return
        buff = source.controller.card("AV_317e", source=source)
        buff.tags[GameTag.DEATHRATTLE] = True
        buff.source = source
        for deathrattle in card.deathrattles:
            buff.additional_deathrattles.append(deathrattle)
        buff.apply(target)
