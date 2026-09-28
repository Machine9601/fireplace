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


# --- RLK_731
class RLK_731:
    """Darkfallen Neophyte"""

    # <b>Battlecry:</b> Spend 2 <b>Corpses</b> to give all minions in your
    # hand +2 Attack.
    play = SpendCorpses(CONTROLLER, 2).then(Buff(FRIENDLY_HAND + MINION, "RLK_731e"))


RLK_731e = buff(atk=2)


# --- RLK_062
class RLK_062:
    """Nerubian Swarmguard"""

    # <b>Taunt</b> <b>Battlecry:</b> Summon two copies of this minion.
    play = Summon(CONTROLLER, ExactCopy(SELF)) * 2


# --- RLK_118
class TombGuardiansSummon(TargetedAction):
    """Summon two Menacing Zombies for TARGET (a player); spend 4 Corpses to
    give them Reborn."""

    TARGET = ActionArg()

    def do(self, source, target):
        game = source.game
        zombies = []
        for _ in range(2):
            for cards in game.queue_actions(source, [Summon(target, "RLK_118t3")])[0]:
                zombies += [c for c in cards if c.zone == Zone.PLAY]
        if not zombies:
            return
        spent = game.queue_actions(source, [SpendCorpses(target, 4)])[0]
        if spent and spent[0]:
            for zombie in zombies:
                if zombie.zone == Zone.PLAY:
                    game.queue_actions(source, [GiveReborn(zombie)])


class RLK_118:
    """Tomb Guardians"""

    # Summon two 2/2 Zombies with <b>Taunt</b>. Spend 4 <b>Corpses</b> to give
    # them <b>Reborn</b>.
    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    play = TombGuardiansSummon(CONTROLLER)


# --- RLK_713
class RLK_713:
    """Lady Deathwhisper"""

    # <b>Deathrattle:</b> Copy all Frost spells in your hand.
    deathrattle = Give(CONTROLLER, ExactCopy(FRIENDLY_HAND + FROST + SPELL))


# --- RLK_740
class RandomSample(Selector):
    """`count` distinct random targets among `child`; `count` may be lazy
    (SpendCorpses.AMOUNT)."""

    def __init__(self, child, count):
        self.child = child
        self.count = count

    def __repr__(self):
        return "RandomSample(%r, %r)" % (self.child, self.count)

    def eval(self, entities, source):
        count = self.count
        if isinstance(count, LazyValue):
            count = count.evaluate(source)
        child_entities = self.child.eval(entities, source)
        return source.game.random.sample(
            child_entities, max(0, min(len(child_entities), count or 0))
        )


class RLK_740:
    """Might of Menethil"""

    # <b>Battlecry:</b> Spend up to 3 <b>Corpses</b>. <b>Freeze</b> that many
    # enemy minions. (At random: the wiki.)
    play = SpendCorpses(CONTROLLER, 3, up_to=True).then(
        Freeze(RandomSample(ENEMY_MINIONS - DEAD, SpendCorpses.AMOUNT))
    )


# --- RLK_745
class RLK_745:
    """Malignant Horror"""

    # <b>Reborn</b> At the end of your turn, spend 4 <b>Corpses</b> to summon a
    # copy of this minion.
    events = OWN_TURN_END.on(
        SpendCorpses(CONTROLLER, 4).then(Summon(CONTROLLER, ExactCopy(SELF)))
    )


# --- RLK_504
class RLK_504:
    """Corpse Bride"""

    # <b>Battlecry:</b> Spend up to 10 <b>Corpses</b> to summon a Risen Groom
    # with <b>Taunt</b> and that much Attack and Health.
    play = SpendCorpses(CONTROLLER, 10, up_to=True).then(
        SummonCustomMinion(
            CONTROLLER, "RLK_506t", 1, SpendCorpses.AMOUNT, SpendCorpses.AMOUNT
        )
    )


class RLK_506t:
    """Risen Groom"""

    # <b>Taunt</b> <i>Doesn't leave a <b>Corpse</b>.</i>
    tags = {enums.LEAVES_NO_CORPSE: True}


# --- RLK_730
class RLK_730:
    """Blood Boil"""

    # <b>Lifesteal</b> Infect all enemy minions. At the end of your turns, they
    # take 2 damage.
    play = Buff(ENEMY_MINIONS, "RLK_730e")


class RLK_730e:
    # The infection: at the end of its caster's turns, 2 damage to the minion,
    # with the Lifesteal of Blood Boil (the CardDefs gives the enchantment
    # LIFESTEAL); the minion itself does not gain Lifesteal.
    tags = {GameTag.LIFESTEAL: False, enums.LIFESTEAL_DAMAGE: True}
    events = OWN_TURN_END.on(Hit(OWNER, 2))


# --- RLK_086
class RLK_086:
    """Frostmourne"""

    # <b>Deathrattle:</b> Summon every minion killed by this weapon.
    # The same effect as the Lich King's Frostmourne (ICC_314t1, the wiki).
    events = Attack(FRIENDLY_HERO, ALL_MINIONS).after(
        Dead(Attack.DEFENDER) & StoringBuff(SELF, "ICC_314t1e", Attack.DEFENDER)
    )


