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


# --- RLK_057
class RLK_057:
    """Dark Transformation"""

    # Transform an Undead into a 4/5 Undead Monstrosity with <b>Rush</b>.
    requirements = {
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_TARGET_WITH_RACE: Race.UNDEAD,
    }
    play = Morph(TARGET, "RLK_057t")


# --- RLK_066
def _blood_rune_card(card):
    """A Blood Rune card that may be generated: at least one Blood rune, and
    not a triple-rune card (they cannot be generated nor Discovered since
    patch 26.0.4, the wiki « Rune »)."""
    blood = card.tags.get(GameTag.COST_BLOOD, 0)
    runes = (
        blood
        + card.tags.get(GameTag.COST_FROST, 0)
        + card.tags.get(GameTag.COST_UNHOLY, 0)
    )
    return blood > 0 and runes < 3


class RLK_066:
    """Hematurge"""

    # <b>Battlecry:</b> Spend a <b>Corpse</b> to <b>Discover</b> a Blood Rune
    # card.
    play = SpendCorpses(CONTROLLER, 1).then(
        DISCOVER(
            RandomCollectible(
                card_class=CardClass.DEATHKNIGHT, custom_filter=_blood_rune_card
            )
        )
    )


# --- RLK_083
class RLK_083:
    """Deathchiller"""

    # After you cast a spell, deal 1 damage to two random enemies.
    events = OWN_SPELL_PLAY.after(Hit(RANDOM(ENEMY_CHARACTERS - DEAD) * 2, 1))


# --- RLK_711
class RLK_711:
    """Vicious Bloodworm"""

    # <b>Battlecry:</b> Give a minion in your hand Attack equal to this
    # minion's Attack. (A target of the hand, CAN_TARGET_CARDS_IN_HAND.)
    requirements = {
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_IF_AVAILABLE: 0,
    }
    play = Buff(TARGET, "RLK_711e", atk=ATK(SELF))


# --- RLK_712
class RLK_712:
    """Blood Tap"""

    # Give all minions in your hand +1/+1. Spend 2 <b>Corpses</b> to give them
    # +1/+1 more.
    play = (
        Buff(FRIENDLY_HAND + MINION, "RLK_712e"),
        SpendCorpses(CONTROLLER, 2).then(Buff(FRIENDLY_HAND + MINION, "RLK_712e")),
    )


RLK_712e = buff(+1, +1)


# --- RLK_015
class RLK_015:
    """Howling Blast"""

    # Deal $3 damage to an enemy and <b>Freeze</b> it. Deal $1 damage to all
    # other enemies.
    requirements = {PlayReq.REQ_ENEMY_TARGET: 0, PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Hit(TARGET, 3), Freeze(TARGET), Hit(ENEMY_CHARACTERS - TARGET, 1)


# --- RLK_087
class RLK_087:
    """Asphyxiate"""

    # Destroy the highest Attack enemy minion. (A tie: at random.)
    play = Destroy(HIGHEST_ATK(ENEMY_MINIONS))


# --- RLK_512
class RLK_512:
    """Glacial Advance"""

    # Deal $4 damage. Your next spell this turn costs (2) less.
    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Hit(TARGET, 4), Buff(CONTROLLER, "RLK_025o")


class RLK_025o:
    # The next spell you cast this turn costs (2) less. (TAG_ONE_TURN_EFFECT)
    update = Refresh(FRIENDLY_HAND + SPELL, {GameTag.COST: -2})
    events = OWN_SPELL_PLAY.on(Destroy(SELF))


