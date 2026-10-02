from ..utils import *


class SummonMinionOfWeaponAttackCost(TargetedAction):
    """Steeldancer: a random minion whose Cost is the weapon's Attack."""

    TARGET = ActionArg()

    def do(self, source, target):
        cost = target.weapon.atk if target.weapon else 0
        # As Evolve: no minion of that Cost, nothing is summoned
        card_set = RandomMinion(cost=cost).find_cards(source)
        if card_set:
            card = source.game.random.choice(card_set)
            source.game.queue_actions(source, [Summon(target, card)])


##
# Minions


class SCH_234:
    """Shifty Sophomore"""

    # <b>Stealth</b> <b>Spellburst:</b> Add a <b>Combo</b> card to your hand.
    spellburst = Give(CONTROLLER, RandomCollectible(combo=True))


class SCH_425:
    """Doctor Krastinov"""

    # <b>Rush</b> Whenever this attacks, give your weapon +1/+1.
    events = Attack(SELF).after(Buff(FRIENDLY_WEAPON, "SCH_425e"))


SCH_425e = buff(+1, +1)


class SCH_426:
    """Infiltrator Lilian"""

    # [x]<b>Stealth</b> <b>Deathrattle:</b> Summon a 4/2 Forsaken Lilian that
    # attacks a random enemy.
    deathrattle = Summon(CONTROLLER, "SCH_426t").then(
        Attack(Summon.CARD, RANDOM(ENEMY_CHARACTERS))
    )


class SCH_519:
    """Vulpera Toxinblade"""

    # Your weapon has +2_Attack.
    update = Refresh(FRIENDLY_WEAPON, buff="SCH_519e")


SCH_519e = buff(atk=2)


##
# Spells


class SCH_305:
    """Secret Passage"""

    # Replace your hand with 4 cards from your deck. Swap back next turn.
    # The swap back is an end of turn effect (hearthstone.wiki.gg): the four
    # cards still in hand are shuffled back into the deck, the cards gained
    # since are kept, and the original hand comes back to their right.
    play = (
        StoringBuff(CONTROLLER, "SCH_305e", FRIENDLY_HAND),
        Remove(FRIENDLY_HAND),
        Give(CONTROLLER, RANDOM(FRIENDLY_DECK, 4)).then(Buff(Give.CARD, "SCH_305e2")),
    )


class SecretPassageShuffleBack(TargetedAction):
    """Secret Passage: shuffle back the cards it took that are still in hand."""

    TARGET = ActionArg()

    def do(self, source, target):
        taken = [
            card
            for card in target.hand
            if any(buff.id == "SCH_305e2" for buff in card.buffs)
        ]
        for card in taken:
            for buff in [b for b in card.buffs if b.id == "SCH_305e2"]:
                buff.remove()
        if taken:
            source.game.queue_actions(source, [Shuffle(target, taken)])


class SCH_305e:
    events = OWN_TURN_END.on(
        SecretPassageShuffleBack(CONTROLLER),
        Give(CONTROLLER, STORE_CARD),
        Destroy(SELF),
    )


class SCH_305e2:
    pass


class SCH_521:
    """Coerce"""

    # Destroy a damaged minion. <b>Combo:</b> Destroy any minion.
    requirements = {
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_DAMAGED_TARGET_UNLESS_COMBO: 0,
    }
    play = Destroy(TARGET)
    combo = Destroy(TARGET)


class SCH_522:
    """Steeldancer"""

    # [x]<b>Battlecry:</b> Summon a random minion with Cost equal to your
    # weapon's Attack.
    # The weapon's Attack (0 without a weapon), not its Cost
    play = SummonMinionOfWeaponAttackCost(CONTROLLER)


class SCH_623:
    """Cutting Class"""

    # [x]Draw 2 cards. Costs (1) less per Attack of your weapon.
    cost_mod = -ATK(FRIENDLY_WEAPON)
    play = Draw(CONTROLLER) * 2


class SCH_706:
    """Plagiarize"""

    # <b>Secret:</b> At the end of your opponent's turn, add copies of the
    # cards they played to your hand.
    secret = EndTurn(OPPONENT).on(Give(CONTROLLER, Copy(CARDS_PLAYED_THIS_TURN)))


##
# Weapons


class SCH_622:
    """Self-Sharpening Sword"""

    # After your hero attacks, gain +1 Attack.
    events = Attack(FRIENDLY_HERO).after(Buff(SELF, "SCH_622e"))


SCH_622e = buff(atk=1)
