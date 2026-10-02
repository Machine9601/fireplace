from hearthstone.enums import Zone

from ..utils import *


class WatchMinionsForKelThuzad(TargetedAction):
    """Headmaster Kel'Thuzad: remember the minions in play as a spell is cast."""

    TARGET = ActionArg()

    def do(self, source, target):
        player = target.controller
        target.kelthuzad_watched = list(player.field) + list(player.opponent.field)


class SummonMinionsDestroyedBySpell(TargetedAction):
    """Headmaster Kel'Thuzad: summon the watched minions the spell destroyed."""

    TARGET = ActionArg()

    def do(self, source, target):
        watched = getattr(target, "kelthuzad_watched", [])
        target.kelthuzad_watched = []
        # Each one comes to its right (rule of a minion's summons): summoned
        # from the last, they end in the order they were watched.
        for minion in reversed(watched):
            if minion.zone == Zone.GRAVEYARD:
                source.game.queue_actions(
                    source, [Summon(target.controller, minion.id)]
                )


def _flatten(result):
    """The cards in what queue_actions returns (lists of lists)."""
    if isinstance(result, (list, tuple)):
        return [card for item in result for card in _flatten(item)]
    return [] if result is None else [result]


class VectusWhelps(TargetedAction):
    """
    Vectus: summon two 1/1 Whelps; each gains the Deathrattle of a friendly
    minion with a Deathrattle that died this game, drawn at random for each.
    """

    TARGET = ActionArg()

    def do(self, source, target):
        for _ in range(2):
            result = source.game.queue_actions(source, [Summon(target, "SCH_162t")])
            whelps = [c for c in _flatten(result) if c.zone == Zone.PLAY]
            dead = [
                card
                for card in target.graveyard
                if card.type == CardType.MINION and card.has_deathrattle
            ]
            if whelps and dead:
                chosen = source.game.random.choice(dead)
                source.game.queue_actions(
                    whelps[0], [CopyDeathrattleBuff(chosen, "SCH_162e")]
                )


##
# Minions


class SCH_162:
    """Vectus"""

    # [x]<b>Battlecry:</b> Summon two 1/1 Whelps. Each gains a
    # <b>Deathrattle</b> from your minions that died this game.
    # Each Whelp copies the Deathrattle of one of them, drawn at random for
    # each (the old script gave both copies to Vectus itself).
    play = VectusWhelps(CONTROLLER)


class SCH_224:
    """Headmaster Kel'Thuzad"""

    # <b>Spellburst:</b> If the spell destroys any minions, summon them.
    # When its player casts a spell, the minions in play (its player's from
    # left to right, then the opponent's) are watched; the Spellburst summons
    # a new copy of each watched minion the spell has destroyed (gone to a
    # graveyard: a transformed or returned minion is not destroyed).
    events = Play(CONTROLLER, SPELL).on(WatchMinionsForKelThuzad(SELF))
    spellburst = SummonMinionsDestroyedBySpell(SELF)


class SCH_428:
    """Lorekeeper Polkelt"""

    # [x]<b>Battlecry:</b> Reorder your deck from the highest Cost card to the
    # lowest Cost card.
    # The top of the deck is its last card: the highest Cost is drawn first.
    def play(self):
        self.controller.deck.sort(key=lambda x: x.cost)


class SCH_717:
    """Keymaster Alabaster"""

    # [x]Whenever your opponent _draws a card, add a copy to_ _your hand that
    # costs (1).
    events = Draw(OPPONENT).on(
        Give(CONTROLLER, Copy(Draw.CARD)).then(Buff(Draw.CARD, "SCH_717e"))
    )


@custom_card
class SCH_717e:
    tags = {
        GameTag.CARDNAME: "Keymaster Alabaster Buff",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
    cost = SET(1)
    events = REMOVED_IN_PLAY


##
# Weapons


class SCH_259:
    """Sphere of Sapience"""

    # [x]At the start of your turn, look at your top card. You can put it on
    # the bottom _and lose 1 Durability.
    events = OWN_TURN_BEGIN.on(
        Find(FRIENDLY_DECK)
        & (
            Choice(CONTROLLER, ["SCH_259t", FRIENDLY_DECK[-1:]]).then(
                Find(Choice.CARD + ID("SCH_259t"))
                & (
                    PutOnBottom(CONTROLLER, FRIENDLY_DECK[-1:]),
                    Hit(SELF, 1),
                )
            )
        )
    )
