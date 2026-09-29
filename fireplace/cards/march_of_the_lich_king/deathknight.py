"""March of the Lich King: the 20 death knight cards that the three decks of
the Tavern Brawl Visions of Sayge ask for (texts of HearthstoneJSON build
253216, the one the official wiki shows).

**Reserved.** These cards are written for that Brawl only: they are not
collectible here (`RESERVED`), so no random pool, no random deck and no
Discover ever offers them; a deck that names them plays them.
"""

from hearthstone.enums import Zone

from ... import enums
from ..utils import *

# The cards of this module: playable when a deck names them, never drawn at
# random (the CardDefs.xml of build 253216 marks them collectible).
RESERVED = {GameTag.COLLECTIBLE: False}


# --- RLK_503
class RLK_503:
    """Body Bagger"""

    # <b>Battlecry:</b> Gain a <b>Corpse</b>.
    tags = RESERVED
    play = GainCorpses(CONTROLLER, 1)


# --- RLK_958
class RLK_958:
    """Skeletal Sidekick"""

    # <b>Battlecry:</b> Give a friendly Undead +2 Attack.
    tags = RESERVED
    requirements = {
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_WITH_RACE: Race.UNDEAD,
        PlayReq.REQ_TARGET_IF_AVAILABLE: 0,
    }
    play = Buff(TARGET, "RLK_958e")


RLK_958e = buff(atk=2)


# --- RLK_708
class RLK_708:
    """Chillfallen Baron"""

    # <b>Battlecry and Deathrattle:</b> Draw a card.
    tags = RESERVED
    play = deathrattle = Draw(CONTROLLER)


# --- LEG_RLK_082
class LEG_RLK_082:
    """Deathbringer Saurfang"""

    # <b>Taunt</b> <b>Deathrattle:</b> Return this to your hand. It costs
    # Health instead of Mana.
    # (The build has no enchantment of its own for it: "Blood of Gods", the one
    # of G'huun the Blood God, says the same, "Costs Health instead of Mana",
    # and goes when the card leaves the hand.)
    tags = RESERVED
    deathrattle = Bounce(SELF).then(Buff(Bounce.TARGET, "DMF_056e"))


# --- RLK_720
class RLK_720:
    """Gnome Muncher"""

    # <b>Taunt</b>, <b>Lifesteal</b> At the end of your turn, attack the lowest
    # Health enemy. (A forced attack on any enemy character, the hero too,
    # chosen at random among the lowest Health; it does not use the attack
    # of the minion itself, the wiki "Force attack".)
    tags = RESERVED
    events = OWN_TURN_END.on(
        Attack(SELF, RANDOM(LOWEST_HEALTH(ENEMY_CHARACTERS - DEAD)))
    )


# --- RLK_025
def _rune_card(rune):
    """A card of the Rune `rune` that may be Discovered: at least one such
    rune, and not a triple-rune card (they cannot be generated nor Discovered
    since patch 26.0.4, the wiki Â« Rune Â»)."""

    def custom_filter(card):
        runes = (
            card.tags.get(GameTag.COST_BLOOD, 0)
            + card.tags.get(GameTag.COST_FROST, 0)
            + card.tags.get(GameTag.COST_UNHOLY, 0)
        )
        return card.tags.get(rune, 0) > 0 and runes < 3

    return custom_filter


class RLK_025:
    """Frost Strike"""

    # Deal $3 damage to a minion. If it dies, <b>Discover</b> a Frost Rune
    # card. (The pool is the collectible death knight cards of the game: the
    # cards of this module are reserved and never in it.)
    tags = RESERVED
    requirements = {PlayReq.REQ_MINION_TARGET: 0, PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Hit(TARGET, 3), Dead(TARGET) & DISCOVER(
        RandomCollectible(
            card_class=CardClass.DEATHKNIGHT,
            custom_filter=_rune_card(GameTag.COST_FROST),
        )
    )


# --- RLK_511
class RLK_511:
    """Harbinger of Winter"""

    # <b>Deathrattle:</b> Draw a Frost spell. (A random one of the deck.)
    tags = RESERVED
    deathrattle = ForceDraw(RANDOM(FRIENDLY_DECK + FROST + SPELL))


# --- LEG_RLK_710
class LEG_RLK_710:
    """Rimefang Sword"""

    # After your hero attacks, reduce the Cost of a spell in your hand by (1).
    # (A random spell of the hand, the wiki "Random".)
    tags = RESERVED
    events = Attack(FRIENDLY_HERO).after(
        Buff(RANDOM(FRIENDLY_HAND + SPELL), "RLK_710e")
    )


RLK_710e = buff(cost=-1)


# --- RLK_709
class RLK_709:
    """Remorseless Winter"""

    # Deal $2 damage to all enemies. Draw a card.
    tags = RESERVED


# --- RLK_223
class RLK_223:
    """Thassarian"""

    # <b>Reborn</b> <b>Battlecry and Deathrattle:</b> Deal 2 damage to a random
    # enemy.
    tags = RESERVED


# --- LEG_RLK_224
class LEG_RLK_224:
    """Overseer Frigidara"""

    # <b>Battlecry:</b> Draw 2 spells. If they're both Frost spells, deal 2
    # damage to all enemies.
    tags = RESERVED


# --- LEG_RLK_039
class LEG_RLK_039:
    """Plagued Grain"""

    # Gain 4 <b>Corpses</b>. Shuffle four Crates into your deck that summon a
    # 2/2 Undead when drawn.
    tags = RESERVED


# --- RLK_061
class RLK_061:
    """Battlefield Necromancer"""

    # At the end of your turn, raise a <b>Corpse</b> as a 1/3 Risen Footman
    # with <b>Taunt</b>.
    tags = RESERVED


# --- LEG_RLK_705
class LEG_RLK_705:
    """Graveyard Shift"""

    # Summon two 1/1 Zombies with <b>Reborn</b>.
    tags = RESERVED


# --- RLK_707
class RLK_707:
    """Grave Strength"""

    # Give your minions +1 Attack. Spend 5 <b>Corpses</b> to give them +3
    # instead.
    tags = RESERVED


# --- LEG_RLK_085
class LEG_RLK_085:
    """Lord Marrowgar"""

    # <b>Battlecry:</b> Raise ALL of your <b>Corpses</b> as 1/1 Risen Golems
    # with <b>Rush</b>. For each that can't fit, give one +2/+2.
    tags = RESERVED


# --- LEG_RLK_744
class LEG_RLK_744:
    """Stitched Giant"""

    # Costs (1) less for each <b>Corpse</b> you've spent this game.
    tags = RESERVED


# --- RLK_048
class RLK_048:
    """Anti-Magic Shell"""

    # Give your minions +1/+1 and <b>Elusive</b>.
    tags = RESERVED


# --- RLK_060
class RLK_060:
    """Army of the Dead"""

    # Raise up to 5 <b>Corpses</b> as 2/2 Risen Ghouls with <b>Rush</b>.
    tags = RESERVED


# --- LEG_RLK_071
class LEG_RLK_071:
    """Patchwerk"""

    # <b>Battlecry:</b> Destroy a random minion in your opponent's hand, deck,
    # and battlefield.
    tags = RESERVED
