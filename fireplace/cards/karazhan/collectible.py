from ..utils import *


class HeroClassOrNeutral(LazyValue):
    """The card classes "suitable for the player's class": neutral and the hero's."""

    def evaluate(self, source):
        return [CardClass.NEUTRAL, CardClass(source.controller.hero.card_class)]


# Prince Malchezaar: five different Legendary minions of his player's class or
# neutral, none already in the starting deck (hearthstone.wiki.gg).
MALCHEZAAR_LEGENDARIES = (
    RandomLegendaryMinion(
        card_class=HeroClassOrNeutral(), exclude=DeDuplicate(STARTING_DECK)
    )
    * 5
)

# "While you have Spell Damage": any Spell Damage, the enemy's Jungle Moonkin included.
HAVE_SPELL_DAMAGE = Find(CONTROLLER + (AttrValue("spellpower") > 0))

# The spells "you've cast this game" (Arcane Giant): a spell countered by
# Counterspell does not count (hearthstone.wiki.gg).
SPELLS_CAST_THIS_GAME = FuncSelector(
    lambda entities, source: [
        card
        for card in source.controller.cards_played_this_game
        if card.type == CardType.SPELL and not card.cant_play
    ]
)


class SummonAtTheFarRight(Summon):
    """
    Moat Lurker: "summons the minion to the far right of the controlling
    player's board" (hearthstone.wiki.gg). A dead minion's Summon would place
    it where the dead minion stood (`_dead_position`), on either board.
    """

    TARGET = ActionArg()
    CARD = ActionArg()

    def do(self, source, target, cards):
        dead_position = getattr(source, "_dead_position", None)
        source._dead_position = None
        try:
            return super().do(source, target, cards)
        finally:
            source._dead_position = dead_position


class BaseCost(LazyNum):
    """The base Cost of the cards in a selector, before any Cost modifier."""

    def __init__(self, selector):
        super().__init__()
        self.selector = selector

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.selector)

    def evaluate(self, source):
        return self.num(sum(e.data.cost for e in self.get_entities(source) if e))


##
# Minions


class KAR_005:
    """Kindly Grandmother"""

    deathrattle = Summon(CONTROLLER, "KAR_005a")


class KAR_006:
    """Cloaked Huntress"""

    update = Refresh(FRIENDLY_HAND + SECRET, {GameTag.COST: SET(0)})


class KAR_009:
    """Babbling Book"""

    play = Give(CONTROLLER, RandomSpell(card_class=CardClass.MAGE))


class KAR_010:
    """Nightbane Templar"""

    powered_up = HOLDING_DRAGON
    play = powered_up & (SummonBothSides(CONTROLLER, "KAR_010a") * 2)


class KAR_021:
    """Wicked Witchdoctor"""

    events = OWN_SPELL_PLAY.on(Summon(CONTROLLER, RandomBasicTotem()))


class KAR_029:
    """Runic Egg"""

    deathrattle = Draw(CONTROLLER)


class KAR_030a:
    """Pantry Spider"""

    play = Summon(CONTROLLER, "KAR_030")


class KAR_033:
    """Book Wyrm"""

    requirements = {
        PlayReq.REQ_ENEMY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_NONSELF_TARGET: 0,
        PlayReq.REQ_TARGET_IF_AVAILABLE_AND_DRAGON_IN_HAND: 0,
        PlayReq.REQ_TARGET_MAX_ATTACK: 3,
    }
    powered_up = HOLDING_DRAGON, Find(ENEMY_MINIONS + (ATK <= 3))
    play = HOLDING_DRAGON & Destroy(TARGET)


class KAR_035:
    """Priest of the Feast"""

    events = OWN_SPELL_PLAY.on(Heal(FRIENDLY_HERO, 3))


class KAR_036:
    """Arcane Anomaly"""

    events = OWN_SPELL_PLAY.after(Buff(SELF, "KAR_036e"))


KAR_036e = buff(health=1)


class KAR_037:
    """Avian Watcher"""

    powered_up = Find(FRIENDLY_SECRETS)
    play = powered_up & Buff(SELF, "KAR_037t")


KAR_037t = buff(+1, +1, taunt=True)


class KAR_041:
    """Moat Lurker"""

    requirements = {
        PlayReq.REQ_TARGET_IF_AVAILABLE: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Destroy(TARGET)
    deathrattle = HAS_TARGET & SummonAtTheFarRight(TARGET_PLAYER, Copy(TARGET))


class KAR_044:
    """Moroes"""

    events = OWN_TURN_END.on(Summon(CONTROLLER, "KAR_044a"))


class KAR_057:
    """Ivory Knight"""

    play = Discover(CONTROLLER, RandomSpell()).then(
        # The base Cost of the discovered card (hearthstone.wiki.gg).
        Give(CONTROLLER, Discover.CARD),
        Heal(FRIENDLY_HERO, BaseCost(Discover.CARD)),
    )


class KAR_061:
    """The Curator"""

    play = (
        ForceDraw(RANDOM(FRIENDLY_DECK + MINION + MURLOC)),
        ForceDraw(RANDOM(FRIENDLY_DECK + DRAGON)),
        ForceDraw(RANDOM(FRIENDLY_DECK + BEAST)),
    )


class KAR_062:
    """Netherspite Historian"""

    powered_up = HOLDING_DRAGON
    play = powered_up & DISCOVER(RandomDragon())


class KAR_065:
    """Menagerie Warden"""

    requirements = {
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_IF_AVAILABLE: 0,
        PlayReq.REQ_TARGET_WITH_RACE: 20,
    }
    powered_up = Find(FRIENDLY_MINIONS + BEAST)
    play = Summon(CONTROLLER, ExactCopy(TARGET))


class KAR_069:
    """Swashburglar"""

    play = Give(CONTROLLER, RandomCollectible(custom_filter=AnotherHeroClass()))


class KAR_070:
    """Ethereal Peddler"""

    play = Buff(FRIENDLY_HAND + OTHER_CLASS_CHARACTER, "KAR_070e")


@custom_card
class KAR_070e:
    tags = {
        GameTag.CARDNAME: "Ethereal Peddler Buff",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.COST: -2,
    }
    events = REMOVED_IN_PLAY


class KAR_089:
    """Malchezaar's Imp"""

    events = Discard(FRIENDLY_HAND).on(Draw(CONTROLLER))


class KAR_092:
    """Medivh's Valet"""

    requirements = {PlayReq.REQ_TARGET_IF_AVAILABLE_AND_MINIMUM_FRIENDLY_SECRETS: 1}
    powered_up = Find(FRIENDLY_SECRETS)
    play = powered_up & Hit(TARGET, 3)


class KAR_094:
    """Deadly Fork"""

    deathrattle = Give(CONTROLLER, "KAR_094a")


class KAR_095:
    """Zoobot"""

    powered_up = Find(
        RANDOM(FRIENDLY_MINIONS + MURLOC)
        | RANDOM(FRIENDLY_MINIONS + DRAGON)
        | RANDOM(FRIENDLY_MINIONS + BEAST)
    )
    play = (
        Buff(RANDOM(FRIENDLY_MINIONS + MURLOC), "KAR_095e"),
        Buff(RANDOM(FRIENDLY_MINIONS + DRAGON), "KAR_095e"),
        Buff(RANDOM(FRIENDLY_MINIONS + BEAST), "KAR_095e"),
    )


KAR_095e = buff(+1, +1)


class KAR_096:
    """Prince Malchezaar"""

    class Deck:
        events = GameStart().on(Shuffle(CONTROLLER, MALCHEZAAR_LEGENDARIES))

    class Hand:
        events = GameStart().on(Shuffle(CONTROLLER, MALCHEZAAR_LEGENDARIES))


class KAR_097:
    """Medivh, the Guardian"""

    play = Summon(CONTROLLER, "KAR_097t")


class KAR_097t:
    """Atiesh"""

    # After the spell, with its final Cost (read when it is cast: once in the
    # graveyard, a spell no longer has its reductions); a full board keeps the
    # Durability, a Cost without minion still loses it (hearthstone.wiki.gg).
    events = [
        OWN_SPELL_PLAY.on(
            SetTags(
                SELF,
                {GameTag.TAG_SCRIPT_DATA_NUM_1: Attr(Play.CARD, GameTag.COST)},
            )
        ),
        OWN_SPELL_PLAY.after(
            FULL_BOARD
            | (
                Summon(
                    CONTROLLER,
                    RandomMinion(cost=Attr(SELF, GameTag.TAG_SCRIPT_DATA_NUM_1)),
                ),
                Hit(SELF, 1),
            )
        ),
    ]


class KAR_114:
    """Barnes"""

    # The copy keeps the enchantments of the card in the deck (patch 12.0).
    play = Summon(CONTROLLER, ExactCopy(RANDOM(FRIENDLY_DECK + MINION))).then(
        Buff(Summon.CARD, "KAR_114e")
    )


class KAR_114e:
    atk = SET(1)
    max_health = SET(1)


class KAR_204:
    """Onyx Bishop"""

    play = Summon(CONTROLLER, Copy(RANDOM(FRIENDLY + KILLED + MINION)))


class KAR_205:
    """Silverware Golem"""

    discard = Summon(CONTROLLER, Copy(SELF))


class KAR_702:
    """Menagerie Magician"""

    powered_up = Find(
        RANDOM(FRIENDLY_MINIONS + MURLOC)
        | RANDOM(FRIENDLY_MINIONS + DRAGON)
        | RANDOM(FRIENDLY_MINIONS + BEAST)
    )
    play = (
        Buff(RANDOM(FRIENDLY_MINIONS + MURLOC), "KAR_702e"),
        Buff(RANDOM(FRIENDLY_MINIONS + DRAGON), "KAR_702e"),
        Buff(RANDOM(FRIENDLY_MINIONS + BEAST), "KAR_702e"),
    )


KAR_702e = buff(+2, +2)


class KAR_710:
    """Arcanosmith"""

    play = Summon(CONTROLLER, "KAR_710m")


class KAR_711:
    """Arcane Giant"""

    cost_mod = -Count(SPELLS_CAST_THIS_GAME)


class KAR_712:
    """Violet Illusionist"""

    update = Find(CURRENT_PLAYER + CONTROLLER) & Refresh(
        FRIENDLY_HERO, {GameTag.IMMUNE: True}
    )


##
# Spells


class KAR_004:
    """Cat Trick"""

    secret = Play(ENEMY, SPELL).after(
        FULL_BOARD | (Reveal(SELF), Summon(CONTROLLER, "KAR_004a"))
    )


class KAR_013:
    """Purify"""

    requirements = {
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }
    play = Silence(TARGET), Draw(CONTROLLER)


class KAR_025:
    """Kara Kazham!"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    play = (
        Summon(CONTROLLER, "KAR_025a"),
        Summon(CONTROLLER, "KAR_025b"),
        Summon(CONTROLLER, "KAR_025c"),
    )


class KAR_026:
    """Protect the King!"""

    requirements = {
        PlayReq.REQ_MINIMUM_ENEMY_MINIONS: 1,
        PlayReq.REQ_NUM_MINION_SLOTS: 1,
    }
    play = Summon(CONTROLLER, "KAR_026t") * Count(ENEMY_MINIONS)


class KAR_073:
    """Maelstrom Portal"""

    play = Hit(ENEMY_MINIONS, 1), Summon(CONTROLLER, RandomMinion(cost=1))


class KAR_075:
    """Moonglade Portal"""

    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Heal(TARGET, 6), Summon(CONTROLLER, RandomMinion(cost=6))


class KAR_076:
    """Firelands Portal"""

    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Hit(TARGET, 5), Summon(CONTROLLER, RandomMinion(cost=5))


class KAR_077:
    """Silvermoon Portal"""

    requirements = {PlayReq.REQ_MINION_TARGET: 0, PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Buff(TARGET, "KAR_077e"), Summon(CONTROLLER, RandomMinion(cost=2))


KAR_077e = buff(+2, +2)


class KAR_091:
    """Ironforge Portal"""

    play = GainArmor(FRIENDLY_HERO, 4), Summon(CONTROLLER, RandomMinion(cost=4))


##
# Weapons


class KAR_028:
    """Fool's Bane"""

    update = Refresh(
        FRIENDLY_HERO,
        {
            GameTag.CANNOT_ATTACK_HEROES: True,
            enums.UNLIMITED_ATTACKS: True,
        },
    )


class KAR_063:
    """Spirit Claws"""

    update = HAVE_SPELL_DAMAGE & Refresh(SELF, {GameTag.ATK: +2})
