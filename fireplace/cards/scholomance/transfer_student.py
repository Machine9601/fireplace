from hearthstone.enums import CardClass, CardSet, CardType

from ..utils import *

##
# Minions

# Transfer Student, « Discover a card from the month's expansions » (D-107 du dépôt
# Hearthstone, WP-182c). Le plateau tiré au sort et ses vingt-cinq versions n'existent plus :
# la carte découvre dans un vivier que la partie lui donne.
#
# `game.month_expansions` : un itérable de `CardSet` ou de noms de `CardSet` (« GANGS »),
# ou d'identifiants de cartes (« CFM_621 »), posé par l'enveloppe. Sans lui (le fork seul, ses
# tests), le vivier est celui de la carte : les cartes collectionnables de Scholomance Academy.
# Ce vivier est donné par la partie, il ne passe pas par `RandomCardPicker.find_cards` : le
# hasard borné au réservoir d'un mode (D-37) ne le coupe pas.

DEFAULT_MONTH_EXPANSIONS = (CardSet.SCHOLOMANCE,)


def month_pool(source):
    """Les identifiants que Transfer Student peut proposer : les cartes collectionnables (serviteur,
    sort, arme) des extensions du mois, de la classe du héros de son joueur ou neutres."""
    from ...cards import db as card_db

    items = getattr(source.game, "month_expansions", None) or DEFAULT_MONTH_EXPANSIONS
    sets, ids = [], []
    for item in items:
        if isinstance(item, CardSet):
            sets.append(item)
        elif isinstance(item, str) and item in CardSet.__members__:
            sets.append(CardSet[item])
        elif isinstance(item, str):
            ids.append(item)
        else:
            sets.append(CardSet(item))
    pool = set(
        card_db.filter(
            collectible=True,
            card_set=sets,
            type=[CardType.MINION, CardType.SPELL, CardType.WEAPON],
        )
    )
    pool.update(i for i in ids if i in card_db)
    hero_class = source.controller.hero.data.card_class
    if hero_class == CardClass.NEUTRAL:
        hero_class = source.controller.starting_hero.data.card_class
    return sorted(
        i
        for i in pool
        if CardClass.NEUTRAL in card_db[i].classes or hero_class in card_db[i].classes
    )


class MonthCard(RandomCardPicker):
    """Une carte au hasard parmi celles des extensions du mois (voir plus haut)."""

    def evaluate(self, source):
        return super().evaluate(source, month_pool(source))


class SCH_199:
    """Transfer Student"""

    # Discover a card from the month's expansions.
    play = DISCOVER(MonthCard())
