"""
Les trésors du raid de Hearthstone (WP-160, règle 649) que CardDefs.xml ne sait pas poser : trois
enchantements **du joueur**, posés au départ de chaque combat comme un effet de départ (règle 472 :
`enchantement.apply(joueur)`), qui valent toute la partie. Aucune carte de CardDefs.xml n'en fait
autant (Fencing Coach, `AT_115e`, s'use au premier pouvoir ; Felfire Deadeye, `YOP_030`, est l'aura
d'un serviteur) ; ce sont donc des cartes à nous (`custom_card`), sans entrée dans CardDefs.xml.
"""

from ..utils import *


@custom_card
class RAID_TRE15e:
    """Pierre de lune (TRE-15) : votre pouvoir héroïque coûte (1) de moins."""

    tags = {
        GameTag.CARDNAME: "Pierre de lune",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
    update = Refresh(FRIENDLY_HERO_POWER, {GameTag.COST: -1})


@custom_card
class RAID_TRE16e:
    """Anneau de Varian (TRE-16) : le premier serviteur que vous jouez dans la partie a Charge.

    Joué depuis la main seulement (`Play`) : un serviteur invoqué ne compte pas. La Charge est celle
    de Tundra Rhino (`DS1_178e`), un enchantement qu'un Silence efface ; l'anneau s'use aussitôt."""

    tags = {
        GameTag.CARDNAME: "Anneau de Varian",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
    events = Play(CONTROLLER, MINION).on(Buff(Play.CARD, "DS1_178e"), Destroy(SELF))


@custom_card
class RAID_TRE17e:
    """Calice de Zul'Gurub (TRE-17) : votre héros a Lifesteal (les dégâts qu'il inflige en
    attaquant soignent votre héros d'autant)."""

    tags = {
        GameTag.CARDNAME: "Calice de Zul'Gurub",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
    update = Refresh(FRIENDLY_HERO, {GameTag.LIFESTEAL: True})
