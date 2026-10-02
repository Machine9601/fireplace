from ..utils import *

##
# Minions


class DMF_060:
    """Umbral Owl"""

    # [x]<b>Rush</b> Costs (1) less for each spell you've cast this game.
    cost_mod = -Count(CARDS_PLAYED_THIS_GAME + SPELL)


class DMF_061:
    """Faire Arborist"""

    # [x]<b>Choose One - </b>Draw a card; or Summon a 2/2 Treant.
    # <b>Corrupt:</b> Do both.
    choose = ("DMF_061a", "DMF_061b")
    play = ChooseBoth(CONTROLLER) & (Draw(CONTROLLER), Summon(CONTROLLER, "DMF_061t2"))
    corrupt_card = "DMF_061t"


class DMF_061a:
    play = Draw(CONTROLLER)


class DMF_061b:
    play = Summon(CONTROLLER, "DMF_061t2")


class DMF_061t:
    play = (
        Draw(CONTROLLER),
        Summon(CONTROLLER, "DMF_061t2"),
    )


class DMF_733:
    """Kiri, Chosen of Elune"""

    # <b>Battlecry:</b> Add a Solar Eclipse and Lunar Eclipse to your hand.
    play = Give(CONTROLLER, "DMF_058"), Give(CONTROLLER, "DMF_057")


class DMF_734:
    """Greybough"""

    # [x]<b>Taunt</b> <b>Deathrattle:</b> Give a random friendly minion
    # "<b>Deathrattle:</b> Summon Greybough."
    deathrattle = Buff(RANDOM_FRIENDLY_MINION, "DMF_734e")


class DMF_734e:
    tags = {GameTag.DEATHRATTLE: True}
    deathrattle = Summon(CONTROLLER, "DMF_734")


class YOP_025:
    """Dreaming Drake"""

    # <b>Taunt</b> <b>Corrupt:</b> Gain +2/+2.
    corrupt_card = "YOP_025t"


##
# Spells


class DMF_057:
    """Lunar Eclipse"""

    # Deal $3 damage to a minion. Your next spell this turn costs (2) less.
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Hit(TARGET, 3), Buff(CONTROLLER, "DMF_057e")


def _spent_by_the_next_spell(self, player, card, *args):
    # The spell that made the enchantment is heard too, after it resolves:
    # it is not "the next spell" (WP-195: Lunar Eclipse lost its reduction at
    # once). self.source is the card that gave the enchantment.
    if card is self.source:
        return []
    return [Destroy(SELF)]


class DMF_057e:
    # "Your next spell this turn": a one-turn effect, which the data does not
    # say (WP-195).
    tags = {GameTag.TAG_ONE_TURN_EFFECT: True}
    update = Refresh(FRIENDLY_HAND + SPELL, {GameTag.COST: -2})
    events = Play(CONTROLLER, SPELL).after(_spent_by_the_next_spell)


class DMF_058:
    """Solar Eclipse"""

    # Your next spell this turn casts twice.
    play = Buff(CONTROLLER, "DMF_058e")


class DMF_058e:
    update = Refresh(CONTROLLER, {GameTag.SPELLS_CAST_TWICE: True})
    events = Play(CONTROLLER, SPELL).after(_spent_by_the_next_spell)


class DMF_075:
    """Guess the Weight"""

    # Draw a card. Guess if your next card costs more or less to draw it.
    # TODO: need to be tested
    def play(self):
        if len(self.controller.deck) > 0:
            card1 = self.controller.deck[-1]
            yield Draw(CONTROLLER)
            if len(self.controller.deck) > 0:
                card2 = self.controller.deck[-1]
                yield Choice(CONTROLLER, ["DMF_075a", "DMF_075a2"]).then(
                    Find(Choice.CARD + ID("DMF_075a"))
                    & (Draw(CONTROLLER) if card1.cost < card2.cost else ()),
                    Find(Choice.CARD + ID("DMF_075a2"))
                    & (Draw(CONTROLLER) if card1.cost > card2.cost else ()),
                )


class DMF_730:
    """Moontouched Amulet"""

    # Give your hero +4 Attack this turn. <b>Corrupt:</b> And gain 6 Armor.
    corrupt_card = "DMF_730t"
    play = Buff(FRIENDLY_HERO, "DMF_730e")


class DMF_730t:
    play = (
        Buff(FRIENDLY_HERO, "DMF_730e"),
        GainArmor(FRIENDLY_HERO, 6),
    )


DMF_730e = buff(atk=4)


class DMF_732:
    """Cenarion Ward"""

    # Gain 8 Armor. Summon a random 8-Cost minion.
    # A minion: RandomCollectible could draw a spell or a weapon (WP-195).
    play = GainArmor(FRIENDLY_HERO, 8), Summon(CONTROLLER, RandomMinion(cost=8))


class YOP_024:
    """Guidance"""

    # Look at two spells. Add one to your hand or <b>Overload:</b> (1) to get
    # both.
    # Two different spells, as cards (WP-195: the choice held two card ids
    # and a card, and Spirit Path gave nothing: "Choice.CARDS - ID" of ids).
    # The data's OVERLOAD tag made every Guidance overload, whatever the
    # choice: only Spirit Path does.
    tags = {GameTag.OVERLOAD: 0}

    def play(self):
        player = self.controller
        spells = [
            player.card(id, source=self) for id in (RandomSpell() * 2).evaluate(self)
        ]
        path = player.card("YOP_024t", source=self)
        yield Choice(CONTROLLER, spells + [path]).then(
            Find(Choice.CARD + ID("YOP_024t"))
            & (Give(CONTROLLER, spells), Overload(CONTROLLER, 1))
            | (Give(CONTROLLER, Choice.CARD))
        )


class YOP_026:
    """Arbor Up"""

    # Summon two 2/2 Treants. Give your minions +2/+1.
    play = Summon(CONTROLLER, "EX1_158t") * 2, Buff(FRIENDLY_MINIONS, "YOP_026e")


YOP_026e = buff(+2, +1)


class YOP_029:
    """Resizing Pouch"""

    # [x]<b>Discover</b> a card with Cost equal to your remaining Mana
    # Crystals.
    # The mana left once the Pouch is paid (WP-195: Count() of a number
    # counted 1, and every card offered cost 1).
    play = DISCOVER(RandomCollectible(cost=CURRENT_MANA(CONTROLLER)))
