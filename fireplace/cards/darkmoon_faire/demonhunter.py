from ..utils import *

##
# Minions


class DMF_217:
    """Line Hopper"""

    # Your <b>Outcast</b> cards cost (1)_less.
    update = Refresh(FRIENDLY_HAND + OUTCAST, {GameTag.COST: -1})


class DMF_222:
    """Redeemed Pariah"""

    # After you play an <b>Outcast</b> card, gain +1/+1.
    # Play(OUTCAST) read OUTCAST as the player: never heard (WP-195).
    events = Play(CONTROLLER, OUTCAST).after(Buff(SELF, "DMF_222e"))


DMF_222e = buff(+1, +1)


class DMF_223:
    """Renowned Performer"""

    # [x]<b>Rush</b> <b>Deathrattle:</b> Summon two __1/1 Assistants with
    # <b>Taunt</b>.__
    deathrattle = Summon(CONTROLLER, "DMF_223t") * 2


class DMF_226:
    """Bladed Lady"""

    # [x]<b>Rush</b> Costs (1) if your hero has 6 or more Attack.
    class Hand:
        update = (ATK(FRIENDLY_HERO) >= 6) & Refresh(SELF, {GameTag.COST: SET(1)})


class DMF_229:
    """Stiltstepper"""

    # [x]<b>Battlecry:</b> Draw a card. If you play it this turn, give your
    # hero +4 Attack this turn.
    play = Draw(CONTROLLER).then(Buff(Draw.CARD, "DMF_229e2"))


class DMF_229e2:
    # Play(OWNER) read the card as the player: never heard (WP-195). The
    # enchantment is a one-turn effect (the data): only this turn.
    events = Play(CONTROLLER, OWNER).after(Buff(FRIENDLY_HERO, "DMF_229e"))


DMF_229e = buff(atk=4)


class DMF_230:
    """Il'gynoth"""

    # [x]<b>Lifesteal</b> Your <b>Lifesteal</b> damages the enemy hero instead
    # of healing you.
    update = Refresh(
        CONTROLLER,
        {
            GameTag.LIFESTEAL_DAMAGES_OPPOSING_HERO: True,
        },
    )


class DMF_231:
    """Zai, the Incredible"""

    # <b>Battlecry:</b> Copy the left- and right-most cards in your hand.
    # "The newly-generated cards will be to the left of the copied cards"
    # (hearthstone.wiki.gg): where they land matters to Outcast (WP-195: both
    # went to the far right). A single card is copied once.
    def play(self):
        player = self.controller
        hand = player.hand
        if not hand:
            return
        outermost = [hand[0]] if len(hand) == 1 else [hand[0], hand[-1]]
        for card in outermost:
            if card.zone != Zone.HAND:
                continue
            copy = player.card(card.id, source=self)
            copy._summon_index = list(player.hand).index(card)
            yield Give(CONTROLLER, copy)
            copy._summon_index = None


class DMF_247:
    """Insatiable Felhound"""

    # <b>Taunt</b> <b>Corrupt:</b> Gain +1/+1 and_<b>Lifesteal</b>.
    corrupt_card = "DMF_247t"


class DMF_248:
    """Felsteel Executioner"""

    # <b>Corrupt:</b> Become a weapon.
    # "corrupted_card" was never read: it never became the weapon (WP-195).
    corrupt_card = "DMF_248t"


class YOP_002:
    """Felsaber"""

    # Can only attack if your hero attacked this turn.
    # Can't attack while the hero has not (WP-195: `|` is "otherwise", which
    # forbade it only after the hero had attacked).
    update = (NUM_ATTACKS_THIS_TURN(FRIENDLY_HERO) == 0) & Refresh(
        SELF, {GameTag.CANT_ATTACK: True}
    )


##
# Spells


class DMF_219:
    """Relentless Pursuit"""

    # Give your hero +4 Attack and <b>Immune</b> this turn.
    play = Buff(FRIENDLY_HERO, "DMF_219e")


DMF_219e = buff(atk=4, immune=True)


class DMF_221:
    """Felscream Blast"""

    # <b>Lifesteal</b>. Deal $1 damage to a minion and its neighbors.
    # A minion is needed (WP-195: no requirement, it was played on nothing).
    requirements = {
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }
    play = Hit(TARGET, 1), Hit(TARGET_ADJACENT, 1)


class DMF_224:
    """Expendable Performers"""

    # Summon seven 1/1 Illidari with <b>Rush</b>. If_they all die this turn,
    # summon seven more.
    # The seven are remembered on the player (WP-195: on the spell, which is
    # in the graveyard, the enchantment never ran), for this turn only (the
    # data: a one-turn effect). If none was summoned, nothing is remembered.
    requirements = {
        PlayReq.REQ_NUM_MINION_SLOTS: 1,
    }

    def play(self):
        player = self.controller
        before = list(player.field)
        yield Summon(CONTROLLER, "BT_036t") * 7
        summoned = [m for m in player.field if m not in before]
        if summoned:
            buff = player.card("DMF_224e", source=self)
            buff.performers = summoned
            yield Buff(CONTROLLER, buff)


class DMF_224e:
    def _all_dead(self, *args):
        performers = getattr(self, "performers", [])
        if performers and all(m.dead or m.zone != Zone.PLAY for m in performers):
            return [Summon(CONTROLLER, "BT_036t") * 7, Destroy(SELF)]
        return []

    events = Death(FRIENDLY + MINION).after(_all_dead)


class DMF_225:
    """Throw Glaive"""

    # Deal $2 damage to a minion. If it dies, add a_temporary copy of this to
    # your hand.
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Hit(TARGET, 2), Dead(TARGET) & Give(CONTROLLER, Copy(SELF)).then(
        GiveTemporary(Give.CARD)
    )


class DMF_249:
    """Acrobatics"""

    # Draw 2 cards. If you play both this turn, draw 2 more.
    # The two cards are remembered on the player (WP-195: on the spell, in the
    # graveyard, the enchantment never ran; and each draw stored one card in
    # its own enchantment, which never counted two). One turn (the data).
    def play(self):
        player = self.controller
        drawn = []
        for _ in range(2):
            before = list(player.hand)
            yield Draw(CONTROLLER)
            drawn += [c for c in player.hand if c not in before]
        if len(drawn) == 2:
            buff = player.card("DMF_249e", source=self)
            buff.drawn = drawn
            yield Buff(CONTROLLER, buff)


class DMF_249e:
    def _both_played(self, player, card, *args):
        # The card being played has no turn_played yet (Play.do sets it last).
        drawn = getattr(self, "drawn", [])
        turn = self.game.turn
        if drawn and all(
            c is card or getattr(c, "turn_played", None) == turn for c in drawn
        ):
            return [Draw(CONTROLLER) * 2, Destroy(SELF)]
        return []

    events = Play(CONTROLLER).after(_both_played)


class YOP_001:
    """Illidari Studies"""

    # <b>Discover</b> an <b>Outcast</b> card. Your next one costs (1) less.
    # The reduction first, then the Discover (with the card given: Discover
    # alone leaves it out of play): an action after a choice in the same tuple
    # is lost (annex A47 of the rules, WP-195), as Scholomance's Studies.
    play = (
        Buff(CONTROLLER, "YOP_001e"),
        DISCOVER(RandomCollectible(outcast=True)),
    )


class YOP_001e:
    update = Refresh(FRIENDLY_HAND + OUTCAST, {GameTag.COST: -1})
    events = Play(CONTROLLER, OUTCAST).after(Destroy(SELF))


##
# Weapons


class DMF_227:
    """Dreadlord's Bite"""

    # [x]<b>Outcast:</b> Deal 1 damage to all enemies.
    outcast = Hit(ENEMY_CHARACTERS, 1)
