from ..utils import *

##
# Minions


class OG_042:
    """Y'Shaarj, Rage Unbound"""

    events = OWN_TURN_END.on(Summon(CONTROLLER, RANDOM(FRIENDLY_DECK + MINION)))


class OG_122:
    """Mukla, Tyrant of the Vale"""

    play = Give(CONTROLLER, "EX1_014t") * 2


class OG_317:
    """Deathwing, Dragonlord"""

    deathrattle = Summon(CONTROLLER, FRIENDLY_HAND + DRAGON)


class OG_318:
    """Hogger, Doom of Elwynn"""

    events = SELF_DAMAGE.on(Summon(CONTROLLER, "OG_318t"))


class OG_338:
    """Nat, the Darkfisher"""

    events = BeginTurn(OPPONENT).on(COINFLIP & Draw(OPPONENT))


class OG_123:
    """Shifter Zerus"""

    class Hand:
        events = OWN_TURN_BEGIN.on(
            Morph(SELF, RandomMinion()).then(Buff(Morph.CARD, "OG_123e"))
        )


class OG_123e:
    class Hand:
        events = OWN_TURN_BEGIN.on(
            Morph(OWNER, RandomMinion()).then(Buff(Morph.CARD, "OG_123e"))
        )

    events = REMOVED_IN_PLAY


class OG_300:
    """The Boogeymonster"""

    events = Attack(SELF, ALL_MINIONS).after(
        Dead(ALL_MINIONS + Attack.DEFENDER) & Buff(SELF, "OG_300e")
    )


OG_300e = buff(+2, +2)


class OG_133:
    """N'Zoth, the Corruptor"""

    # In the order they died. "If there is not enough room on the board to
    # summon a copy of each, N'Zoth will randomly choose which ones to summon"
    # (hearthstone.wiki.gg): as many as there is room for, drawn at random,
    # still in the order they died.
    def play(self):
        dead = list((FRIENDLY + KILLED + MINION + DEATHRATTLE).eval(self.game, self))
        room = self.controller.minion_slots
        if len(dead) > room:
            kept = self.game.random.sample(dead, room)
            dead = [card for card in dead if card in kept]
        if dead:
            yield Summon(CONTROLLER, [card.id for card in dead])


class CastSpellWhateverBecomesOfTheCaster(CastSpell):
    """
    CastSpell, but it goes on when the minion that casts is destroyed,
    Silenced, transformed or returned to the hand: Yogg-Saron, since patch
    16.6 (hearthstone.wiki.gg).
    """

    def do(self, source, card, targets):
        player = source.controller
        old_choice = player.choice
        player.choice = None
        if card.twinspell:
            source.game.queue_actions(card, [Give(player, card.twinspell_copy)])
        if card.must_choose_one:
            card = source.game.random.choice(card.choose_cards)
        for target in targets:
            if card.requires_target() and not target:
                if len(card.targets) > 0:
                    if target not in card.targets:
                        target = self.choose_target(source, card)
                else:
                    return
            card.target = target
            card.zone = Zone.PLAY
            source.game.manager.targeted_action(self, source, card, target)
            source.game.queue_actions(card, [Battlecry(card, card.target)])
            while player.choice:
                player.choice.choose(source.game.random.choice(player.choice.cards))
            while player.opponent.choice:
                player.opponent.choice.choose(
                    source.game.random.choice(player.opponent.choice.cards)
                )
            player.choice = old_choice


class OG_134:
    """Yogg-Saron, Hope's End"""

    # "Cast a random spell for each spell you've cast this game": the spells
    # played from the hand, a spell countered by Counterspell excepted, and
    # none cast by an effect. At most 30 (hearthstone.wiki.gg). Since patch
    # 16.6, Yogg-Saron goes on when it is destroyed, Silenced, transformed or
    # returned to the hand.
    def play(self):
        times = len(
            [
                card
                for card in self.controller.cards_played_this_game
                if card.type == CardType.SPELL and not card.cant_play
            ]
        )
        for _ in range(min(times, 30)):
            if self.game.ended:
                break
            yield CastSpellWhateverBecomesOfTheCaster(RandomSpell())
            yield Deaths()


class OG_280:
    """C'Thun"""

    play = Hit(RANDOM_ENEMY_CHARACTER, 1) * ATK(SELF)


class OG_131:
    """Twin Emperor Vek'lor"""

    play = CHECK_CTHUN & Summon(CONTROLLER, "OG_319")
