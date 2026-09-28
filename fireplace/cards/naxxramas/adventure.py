from ..blackrock.adventure import ArmorBroken
from ..utils import *

##
# Hero Powers


class NAX1_04:
    """Skitter"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    activate = Summon(CONTROLLER, "NAX1_03")


class NAX1h_04:
    """Skitter (Heroic)"""

    activate = Summon(CONTROLLER, "NAX1h_03")


class NAX2_03:
    """Rain of Fire"""

    activate = Hit(RANDOM_ENEMY_MINION, 1) * Count(ENEMY_HAND)


class NAX2_03H:
    """Rain of Fire (Heroic)"""

    activate = Hit(RANDOM_ENEMY_MINION, 1) * Count(ENEMY_HAND)


class NAX2_05:
    """Worshipper"""

    update = CurrentPlayer(CONTROLLER) & Refresh(FRIENDLY_HERO, {GameTag.ATK: +1})


class NAX2_05H:
    """Worshipper (Heroic)"""

    update = CurrentPlayer(CONTROLLER) & Refresh(FRIENDLY_HERO, {GameTag.ATK: +3})


class NAX3_02:
    """Web Wrap"""

    requirements = {PlayReq.REQ_MINIMUM_ENEMY_MINIONS: 1}
    activate = Bounce(RANDOM_ENEMY_MINION)


class NAX3_02H:
    """Web Wrap"""

    activate = Bounce(RANDOM_ENEMY_MINION * 2)


class NAX4_04:
    """Raise Dead"""

    events = Death(ENEMY + MINION).on(Summon(CONTROLLER, "NAX4_03"))


class NAX4_04H:
    """Raise Dead (Heroic)"""

    events = Death(ENEMY + MINION).on(Summon(CONTROLLER, "NAX4_03H"))


class NAX5_02:
    """Eruption"""

    requirements = {PlayReq.REQ_MINIMUM_ENEMY_MINIONS: 1}
    activate = Hit(ENEMY_MINIONS[0], 2)


class NAX5_02H:
    """Eruption (Heroic)"""

    requirements = {PlayReq.REQ_MINIMUM_ENEMY_MINIONS: 0}
    activate = Hit(ENEMY_MINIONS[0], 3)


# The prohibited cards (the wiki): Loatheb, "If summoned, Kel'Thuzad will
# destroy Alexstrasza, refund no mana"; the Four Horsemen, "Playing Doomsayer
# will cause the minion to be instantly destroyed, while Equality will simply
# fail to take effect. No mana will be refunded". "If you manage to transform
# [the boss] into a different hero [...] you will be able to play [them]
# normally": the rule lives on the boss's Hero Power.
PROHIBITED_MINION = Counter(Play.CARD), Destroy(Play.CARD)


class NAX6_02:
    """Necrotic Aura"""

    activate = Hit(ENEMY_HERO, 3)
    events = Play(OPPONENT, ID("EX1_561")).on(*PROHIBITED_MINION)


class NAX6_02H:
    """Necrotic Aura (Heroic)"""

    activate = Hit(ENEMY_HERO, 3)
    events = Play(OPPONENT, ID("EX1_561")).on(*PROHIBITED_MINION)


class NAX7_03:
    """Unbalancing Strike"""

    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    activate = Hit(TARGET, 3)


class NAX7_03H:
    """Unbalancing Strike (Heroic)"""

    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    activate = Hit(TARGET, 4)


class NAX8_02:
    """Harvest"""

    activate = Draw(CONTROLLER)


class NAX8_02H:
    """Harvest (Heroic)"""

    activate = Draw(CONTROLLER), GainMana(CONTROLLER, 1)


class NAX9_06:
    """Unholy Shadow"""

    activate = Draw(CONTROLLER) * 2
    events = (
        Play(OPPONENT, ID("NEW1_021")).on(*PROHIBITED_MINION),
        Play(OPPONENT, ID("EX1_619")).on(Counter(Play.CARD)),
    )


class NAX10_03:
    """Hateful Strike"""

    requirements = {PlayReq.REQ_MINION_TARGET: 0, PlayReq.REQ_TARGET_TO_PLAY: 0}
    activate = Destroy(TARGET)


class NAX10_03H:
    """Hateful Strike (Heroic)"""

    requirements = {PlayReq.REQ_MINION_TARGET: 0, PlayReq.REQ_TARGET_TO_PLAY: 0}
    activate = Destroy(TARGET)


class NAX11_02:
    """Poison Cloud"""

    activate = Hit(ALL_MINIONS, 1).then(
        Dead(Hit.TARGET) & Summon(CONTROLLER, "NAX11_03")
    )


class NAX11_02H:
    """Poison Cloud (Heroic)"""

    activate = Hit(ENEMY_CHARACTERS, 2).then(
        Dead(Hit.TARGET) & Summon(CONTROLLER, "NAX11_03")
    )


class NAX12_02:
    """Decimate"""

    # "Change the Health of all minions to 1." (heroic: "of enemy minions")
    requirements = {PlayReq.REQ_MINIMUM_TOTAL_MINIONS: 1}
    activate = Buff(ALL_MINIONS, "NAX12_02e")


class NAX12_02H:
    """Decimate (Heroic)"""

    requirements = {PlayReq.REQ_MINIMUM_ENEMY_MINIONS: 1}
    activate = Buff(ENEMY_MINIONS, "NAX12_02e")


class NAX12_02e:
    max_health = SET(1)


class NAX13_02:
    """Polarity Shift"""

    activate = Buff(ALL_MINIONS, "NAX13_02e")


NAX13_02e = AttackHealthSwapBuff()


class NAX14_02:
    """Frost Breath"""

    activate = Destroy(ENEMY_MINIONS - FROZEN - ADJACENT(ID("NAX14_03")))


# Kel'Thuzad (the wiki): "He starts in Phase 1 and will enter Phase 2
# immediately as soon as all of his Armor is gone [...] Kel'Thuzad is also
# capable of switching to Phase 2 preemptively [...] at turn 11. When
# Kel'Thuzad enters Phase 2, his hero power will change to Chains and he will
# summon 2 Guardian of Icecrown." The guides: 10 Armor, 20 in heroic; the
# Guardians are 3/3, 5/5 in heroic.


class KelThuzadPhase2(TargetedAction):
    """Phase 2 of Kel'Thuzad (target, the boss player): Chains, and two
    Guardians of Icecrown."""

    TARGET = ActionArg()

    def do(self, source, target):
        if getattr(target, "kelthuzad_phase", 1) != 1:
            return
        target.kelthuzad_phase = 2
        heroic = source.id.endswith("H")
        guardian = "NAX15_03t" if heroic else "NAX15_03n"
        return source.game.queue_actions(
            source,
            [
                Summon(target, "NAX15_04H" if heroic else "NAX15_04"),
                Summon(target, guardian) * 2,
            ],
        )


class KelThuzadTurn(TargetedAction):
    """At the start of his turn, from turn 11: Phase 2."""

    TARGET = ActionArg()

    def do(self, source, target):
        if source.game.turn >= 11:
            return source.game.queue_actions(source, [KelThuzadPhase2(target)])


class NAX15_02:
    """Frost Blast"""

    activate = Hit(ENEMY_HERO, 2), Freeze(ENEMY_HERO)
    update = ArmorBroken() & KelThuzadPhase2(CONTROLLER)
    events = OWN_TURN_BEGIN.on(KelThuzadTurn(CONTROLLER))


class NAX15_02H:
    """Frost Blast (Heroic)"""

    activate = Hit(ENEMY_HERO, 3), Freeze(ENEMY_HERO)
    update = ArmorBroken() & KelThuzadPhase2(CONTROLLER)
    events = OWN_TURN_BEGIN.on(KelThuzadTurn(CONTROLLER))


class NAX15_04:
    """Chains"""

    # "Take control of a random enemy minion until end of turn."
    requirements = {PlayReq.REQ_MINIMUM_ENEMY_MINIONS: 1}
    activate = Steal(RANDOM_ENEMY_MINION).then(Buff(Steal.TARGET, "NAX15_04a"))


class NAX15_04a:
    # "Until end of turn" (as Shadow Madness gives it back).
    events = (
        TURN_END.on(Destroy(SELF), Steal(OWNER, OPPONENT)),
        Silence(OWNER).on(Steal(OWNER, OPPONENT)),
    )


class NAX15_04H:
    """Chains (Heroic)"""

    requirements = {PlayReq.REQ_MINIMUM_ENEMY_MINIONS: 1}
    activate = Steal(RANDOM_ENEMY_MINION)


##
# Minions


class FP1_006:
    """Deathcharger"""

    deathrattle = Hit(FRIENDLY_HERO, 3)


class NAX8_03:
    """Unrelenting Trainee"""

    deathrattle = Summon(OPPONENT, "NAX8_03t")


class NAX8_03t:
    """Spectral Trainee"""

    events = OWN_TURN_BEGIN.on(Hit(FRIENDLY_HERO, 1))


class NAX8_04:
    """Unrelenting Warrior"""

    deathrattle = Summon(OPPONENT, "NAX8_04t")


class NAX8_04t:
    """Spectral Warrior"""

    events = OWN_TURN_BEGIN.on(Hit(FRIENDLY_HERO, 1))


class NAX8_05:
    """Unrelenting Rider"""

    deathrattle = Summon(OPPONENT, "NAX8_05t")


class NAX8_05t:
    """Spectral Rider"""

    events = OWN_TURN_BEGIN.on(Hit(FRIENDLY_HERO, 1))


class NAX9_02:
    """Lady Blaumeux"""

    update = Refresh(FRIENDLY_HERO, {GameTag.CANT_BE_DAMAGED: True})


class NAX9_02H:
    """Lady Blaumeux (Heroic)"""

    update = Refresh(FRIENDLY_HERO, {GameTag.CANT_BE_DAMAGED: True})


class NAX9_03:
    """Thane Korth'azz"""

    update = Refresh(FRIENDLY_HERO, {GameTag.CANT_BE_DAMAGED: True})


class NAX9_03H:
    """Thane Korth'azz (Heroic)"""

    update = Refresh(FRIENDLY_HERO, {GameTag.CANT_BE_DAMAGED: True})


class NAX9_04:
    """Sir Zeliek"""

    update = Refresh(FRIENDLY_HERO, {GameTag.CANT_BE_DAMAGED: True})


class NAX9_04H:
    """Sir Zeliek (Heroic)"""

    update = Refresh(FRIENDLY_HERO, {GameTag.CANT_BE_DAMAGED: True})


class NAX14_03:
    """Frozen Champion"""

    update = Refresh(SELF, {GameTag.FROZEN: True})


class NAXM_001:
    """Necroknight"""

    deathrattle = Destroy(SELF_ADJACENT)


class NAXM_002:
    """Skeletal Smith"""

    deathrattle = Destroy(ENEMY_WEAPON)


##
# Spells


class NAX1_05:
    """Locust Swarm"""

    play = Hit(ENEMY_MINIONS, 3), Heal(FRIENDLY_HERO, 3)


class NAX3_03:
    """Necrotic Poison"""

    requirements = {PlayReq.REQ_MINION_TARGET: 0, PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Destroy(TARGET)


class NAX4_05:
    """Plague"""

    play = Destroy(ALL_MINIONS - ID("NAX4_03") - ID("NAX4_03H"))


class NAX5_03:
    """Mindpocalypse"""

    play = Draw(ALL_PLAYERS) * 2, GainMana(ALL_PLAYERS, 1)


class NAX6_03:
    """Deathbloom"""

    requirements = {PlayReq.REQ_MINION_TARGET: 0, PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Hit(TARGET, 5), Summon(CONTROLLER, "NAX6_03t")


class NAX6_03t:
    deathrattle = Buff(ENEMY_MINIONS, "NAX6_03te")


NAX6_03te = buff(atk=8)


class NAX6_04:
    """Sporeburst"""

    play = Hit(ENEMY_MINIONS, 1), Summon(CONTROLLER, "NAX6_03t")


class NAX7_05:
    """Mind Control Crystal"""

    play = Steal(ENEMY_MINIONS + ID("NAX7_02"))


class NAX9_07:
    """Mark of the Horsemen"""

    play = Buff(FRIENDLY + (WEAPON | MINION), "NAX9_07e")


NAX9_07e = buff(+1, +1)


class NAX11_04:
    """Mutating Injection"""

    requirements = {PlayReq.REQ_MINION_TARGET: 0, PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Buff(TARGET, "NAX11_04e")


NAX11_04e = buff(+4, +4, taunt=True)


class NAX12_04:
    """Enrage"""

    play = Buff(SELF, "NAX12_04e")


NAX12_04e = buff(atk=6)


class NAX13_03:
    """Supercharge"""

    play = Buff(FRIENDLY_MINIONS, "NAX13_03e")


NAX13_03e = buff(health=2)


class NAX14_04:
    """Pure Cold"""

    play = Hit(ENEMY_HERO, 8), Freeze(ENEMY_HERO)


##
# Weapons


class NAX7_04:
    """Massive Runeblade"""

    update = Attacking(FRIENDLY_HERO, HERO) & Refresh(SELF, {GameTag.ATK: +5})


class NAX7_04H:
    """Massive Runeblade (Heroic)"""

    update = Attacking(FRIENDLY_HERO, HERO) & Refresh(SELF, {GameTag.ATK: +10})


class NAX9_05:
    """Runeblade"""

    update = Find(ID("NAX9_02") | ID("NAX9_03") | ID("NAX9_04")) & Refresh(
        SELF, {GameTag.ATK: +3}
    )


class NAX9_05H:
    """Runeblade (Heroic)"""

    update = Find(ID("NAX9_02H") | ID("NAX9_03H") | ID("NAX9_04H")) & Refresh(
        SELF, {GameTag.ATK: +6}
    )


class NAX10_02:
    """Hook"""

    deathrattle = Give(CONTROLLER, "NAX10_02")


class NAX10_02H:
    """Hook (Heroic)"""

    deathrattle = Give(CONTROLLER, "NAX10_02H")


class NAX12_03:
    """Jaws"""

    events = Death(MINION + DEATHRATTLE).on(Buff(SELF, "NAX12_03e"))


class NAX12_03H:
    """Jaws (Heroic)"""

    events = Death(MINION + DEATHRATTLE).on(Buff(SELF, "NAX12_03e"))


NAX12_03e = buff(atk=2)
