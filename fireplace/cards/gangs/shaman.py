from ..utils import *

##
# Minions


class CFM_061:
    """Jinyu Waterspeaker"""

    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Heal(TARGET, 6)


class CFM_312(JadeGolemUtils):
    """Jade Chieftain"""

    play = SummonJadeGolem(CONTROLLER).then(Taunt(SummonJadeGolem.CARD))


class CFM_324:
    """White Eyes"""

    deathrattle = Shuffle(CONTROLLER, "CFM_324t")


class CFM_697:
    """Lotus Illusionist"""

    events = Attack(SELF, ENEMY_HERO).after(Morph(SELF, RandomMinion(cost=6)))


##
# Spells


class CFM_310:
    """Call in the Finishers"""

    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    play = Summon(CONTROLLER, "CFM_310t") * 4


class CFM_313:
    """Finders Keepers"""

    # Jamais lui-même (corrigé dans le jeu en 2020, avant le patch 21.8 ; hearthstone.wiki.gg).
    play = DISCOVER(
        RandomCollectible(card_class=CardClass.SHAMAN, overload=True, exclude=SELF)
    )


class DevolveOne(TargetedAction):
    """Devolve : un serviteur qui coûte (1) de moins ; sans serviteur à ce coût, le coût le
    plus proche, le plus bas d'abord à égalité ; un serviteur à 0 en devient un à 0
    (hearthstone.wiki.gg : « 0-mana minions will transform into other 0-mana minions »)."""

    TARGET = ActionArg()

    def do(self, source, target):
        wanted = max(0, target.cost - 1)
        for cost in sorted(range(0, 31), key=lambda c: (abs(c - wanted), c)):
            card_set = RandomMinion(cost=cost).find_cards(source)
            if card_set:
                card = source.game.random.choice(card_set)
                return source.game.queue_actions(source, [Morph(target, card)])[0]


class CFM_696:
    """Devolve"""

    requirements = {PlayReq.REQ_HERO_TARGET: 0}
    play = DevolveOne(ENEMY_MINIONS)


class CFM_707(JadeGolemUtils):
    """Jade Lightning"""

    requirements = {PlayReq.REQ_TARGET_IF_AVAILABLE: 0}
    play = Hit(TARGET, 4), SummonJadeGolem(CONTROLLER)


##
# Weapons


class CFM_717(JadeGolemUtils):
    """Jade Claws"""

    play = SummonJadeGolem(CONTROLLER)
